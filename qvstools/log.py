"""Tools for reading logfiles and working out dependencies."""
import re
import sys
import os
import codecs
from qvstools.qvd import QVD
from qvstools.regex_store import searches
from qvstools.text import known_encodings, print_progress

def detect_log_encoding(textfile,encodings):
	"""Tries to open textfile with a variety of encodings and returns the one that works"""
	if len(encodings) == 1: #Assume that it's the only valid one:
		return encodings

	with open(textfile,'rb') as f:
		f.seek(0)	#Could be altered to provide a differnt start position, but fine as is I think.
		test_bytes = f.read(140)
		
		bom_le = codecs.BOM_UTF16_LE
		bom_be = codecs.BOM_UTF16_BE 

		if test_bytes.startswith(bom_le):
			return 'utf-16'
		elif test_bytes.startswith(bom_be):
			return 'utf-16'
		else:
			for e in encodings:
				#print(e)
				f.seek(0)	#Could be altered to provide a differnt start position, but fine as is I think.
				test_bytes = f.read(140)
				try:
					test_string = test_bytes.decode(e,'strict').encode('utf-8')
					# if '\x00' in test_string:
					# 	print('NULL CHAR')
					# 	pass
					# else:
					return e

				except (UnicodeDecodeError,UnicodeEncodeError):
					#print('ERROR')
					pass
	return None

def decode_log_with_detected(textfile):
	"""Uses :func:`detect_encoding <qvstools.text.detect_encoding>` to get encoding and returns a unicode string of the text file"""
	encoding  = detect_log_encoding(textfile,known_encodings['log'])
	print('Decoding with {0}'.format(encoding))
	with open(textfile,'r',encoding=encoding,errors='replace') as f:
		fulltext = f.read()
		#print(fulltext[0:100])
		return fulltext

class LogFile:
	"""Parses a qlikview logfile and creates an object with it's info more easliy accessible."""
	def __init__(self,textfile):
		"""Take a Logfile and turn it into an object."""
		self.path = textfile
		self.dir  = os.path.dirname(textfile)
		self.lines = self.parse_logfile(textfile)
		self.tag_file_lines()


	@staticmethod
	def parse_logfile(textfile):
		""""Parses the logfile and dict for each line.

		Each line is turned into a dict with the following keys::

			{
			'date':'date of execution',
			'time':'time of execution',
			'op':'operation number of the line if present',
			'text':'the remainder of the line'
			}
		"""
		fulltext = decode_log_with_detected(textfile)
		parsed = []
		lines = fulltext.split('\n')
		nlines = len(lines)
		i = 0
		for l in lines:
			#print_progress (i, nlines)
			i += 1
			#First 10 chars are the date:
			date = l[0:10]
			#Gap of 1 char, then next 8 are time.
			time = l[11:19]
			#22-26  are operation no:
			op = l[21:25]
			#the rest is unknown...
			rest = l[26:].strip()
			lp = {
				'date':date,
				'time':time,
				'op':op,
				'text':rest
				}
			parsed.append(lp)
		return parsed

	def tag_file_lines (self):
		print('Scanning logfile for data files mentioned.')

		#Tag lines that reference qvds or other files within the logfile.

		filesearch = searches['filesearchstring2']	#Finds a qvd. Returns the name in the capture group.
		storesearch = searches['store_statement']
		dirsearch = searches['directory_statement']
		
		matchlines = []
		optype = 'LOAD'	#By default expect matches to be load statements.
		workingdir = self.dir
		no_of_lines = len(self.lines)
		counter = 0
		for line in range(0,no_of_lines - 1):
			#print_progress(counter,no_of_lines)
			counter += 1 
			linetext = self.lines[line]['text']
			if re.search(storesearch,linetext):
				optype = 'STORE'
			if linetext.strip().upper().startswith('DIRECTORY'):
				workingdir = linetext[10:].strip()
			s = re.search(filesearch,linetext)
			file = None
			if s and isinstance(s.group(1),str) and isinstance(s.group(2),str):
				file = s.group(1) + '.' + s.group(2)
			elif s and isinstance(s.group(3),str) and isinstance(s.group(4),str):
				file = s.group(3) + '.' + s.group(4)
			if file:
				self.lines[line]['file'] = file.replace('\\\\','\\')
				self.lines[line]['load'] = optype == 'LOAD'
				self.lines[line]['store'] = optype == 'STORE'
				self.lines[line]['workingdir'] = workingdir
				matchlines.append(file)
			#reset optype
				optype = 'LOAD'
		return matchlines

	def get_file_lines(self):
		"""Returns a list of the files found by tag_file_lines."""
		files_touched = [line for line in self.lines if 'file' in line.keys()]
		return files_touched

	def find_file(self,line):
		#Checks if the file exists and returns its absolute path.
		
		f = line['file']
		wd = line['workingdir']
		ld = self.dir
		#print('FILE IS:' + f)
		#print('WDIR IS:' + wd)
		#print('LDIR IS' + ld)		
		if os.path.isabs(f):
			#print('ABSOLUTE PATH')
			path = os.path.abspath(f)
		elif os.path.isabs(wd):
			#print('ABSOLUTE WD')
			path = os.path.abspath(os.path.join(wd,f))
		else:
			#print('RELATIVE WD')
			path = os.path.abspath(os.path.join(ld,wd,f))
			
		#print('PATH IS:' + path)
		if os.path.isabs(path):
			if os.path.isfile(path):
				return (path)
		else:
			rootpath = self.dir
			#print('searching in {0}'.format(rootpath))
			joined = os.path.abspath(os.path.join(rootpath,path))
			if os.path.isfile(joined):
				return joined
			else:
				return None


def build_dependency_graph(path,depth=100,remap_paths=False,basepaths_only=False,blacklist=[]):
	"""Recursively looks through log files to build a dependency graph.
	Steps:
		1. Start with the logfile, and find all the files it generates.
		2. For the qvd files, find the creator doc for those files, and see if *that* file has a logfile.
		3. If it does, see step 1.
		4. Once all your logfiles have been searched through, write out the dependency graph in a structured format.

	The dependency graph is returned in the following format::

		{
		'depth':'depth of recursion',
		'maxfiles': 'maximum number of files scanned',
		'qvw': [list of qvds scanned or named as creatordoc]
		'qvd': [list of each qvd file found],
		'otherfiles': [list ofeach non qvd data file found]
		'creatordocs': [list of tuples (qvd,creatordoc) for each qvd file found],
		'userdocs':[list of tuples (userdoc,qvd) for each qvd file found],
		'triplets':[list of tuples (userdoc,qvd,creatordoc) for each qvd file found]
		}

	:param depth: The maximum number of logfiles to scan.
	:param remap_paths: A dict of paths to replace, where key is the path to replace and value is it's relacement.
	This is useful for remapping drive names where different users have relaoded different qvws, resulting in mixed drivenames and filepaths.
	"""

	def gather_deps(logfile_input):
		"""Returns a tuple for each dependency: (qvw_loaded_by,file_loaded,qvd_created_by)"""
		if not os.path.isfile(logfile_input):
			print('Could not find logfile: {0}'.format(logfile_input))
			return None
		else:
			print('parsing logfile: {0}'.format(logfile_input))
			qvw = logfile_input[0:-4]
			lf = LogFile(logfile_input)
			deps = []
			print('Gathering info on found files:')
			i = 0
			nlines = len(lf.get_file_lines())
			for l in lf.get_file_lines():
				#print_progress(i, nlines)
				i += 1
				deps_triplet = [qvw,'None','None']
				l_file = lf.find_file(l)
				if l_file:
					deps_triplet[1] = l_file
					if l_file.endswith('.qvd'):
						creatordoc = QVD(l_file).CreatorDoc
						deps_triplet[2] = creatordoc
					else:
						pass
				else:
					deps_triplet[1] = l['file'] + '(UNFOUND)'
				deps_triplet = tuple(deps_triplet)
				deps.append(deps_triplet)
			
			#Print some handy output:
			qvds = set([x[1] for x in deps])
			creatordocs = set([x[2] for x in deps])
			print('Creator Docs Found:')
			for x in creatordocs:
				print(x)
			print('Data Files Found:')
			for x in qvds:
				print(x)
			return deps

	def remap_path(abspath):
		if remap_paths:
			for key, value in remap_paths.items():
				if abspath.startswith(key):
					return value + abspath[len(key):]
		return abspath

	input_error_message = 'This function takes a logfile or a qvw file (that has a log file associated with it). Did you supply a valid qvw or log file?'
	#Sense check inut:
	if path.endswith('.log'):
		if os.path.isfile(path):
			logfile_input = os.path.abspath(path)
			root_qvw = os.path.abspath(path[0:-4]+'.qvw')
		else:
			print(input_error_message,'NOT LOG')
			return
	elif path.endswith('.qvw'):
		if os.path.isfile(path):
			logfile_input = os.path.abspath(path + '.log')
			root_qvw = os.path.abspath(path)
		else:
			print(input_error_message,'NOT QVW')
			return
	else:
		print(input_error_message,'NEITHER')
		return

	deps_all = []
	counter_depth  = 0
	counter_files = 0
	logfiles_working = [logfile_input]
	logfiles_done = []

	##Results objects:
	r_qvd = [] 		# QVDs (abspath)
	r_qvw = [] 	# QVWs (abspath)
	r_other = [] 	# Other files (excel,csv) (abspath)
	r_creatordocs = [] # List of tuples: (qvd,creatodoc) 
	r_userdocs = [] #List of tuples (qvw,file )
	r_triplets = [] #List of tuples (userdoc,file,creatordoc)

	while counter_depth < depth and len(logfiles_working) > 0:
		counter_depth += 1
		# Pop a logfile from the list to work on.
		l = logfiles_working.pop()
		print('\n\nGathering deps for {0}'.format(l))

		#Append it to logfiles_done so it won't get done again.
		logfiles_done.append(l)

		#Add the associated qvw to our results.
		qvw_current = l[0:-4]
		r_qvw.append(qvw_current)

		#Gather deps on it.
		deps = gather_deps(l)

		if remap_paths and deps:
			deps = [tuple(remap_path(x) for x in d) for d in deps]
			
		#If it has any add them to our results.
		if deps:
			# Add the deps triplets to the results.
			r_qvd += [d[1] for d in deps if d[1].endswith('.qvd')]
			r_other += [d[1] for d in deps if not d[1].endswith('.qvd')]
			r_userdocs += [(d[0],d[1]) for d in deps]
			r_creatordocs += [(d[1],d[2]) for d in deps]
			r_triplets += [(d[0], d[1], d[2]) for d in deps]
			r_qvw += [d[2] for d in deps if d[2] not in r_qvw]

			#Add any new creatordocs to logfiles_working.
			for d in deps:
				dlog = d[2]+'.log'
				if dlog not in logfiles_done and dlog not in logfiles_working and os.path.basename(d[2]) not in blacklist:
					if  os.path.isfile(dlog):
						logfiles_working.append(dlog)
					else:
						print('Missing Logfile: {0}'.format(dlog))
						logfiles_working.append(dlog)

		print('Finished with {0}'.format(l))
		# print('Still to do:')
		# for f in logfiles_working:
		# 	print(f)
		

	if basepaths_only:
		r_qvd = [os.path.basename(x) for x in r_qvd]
		r_qvw = [os.path.basename(x) for x in r_qvw]
		r_other = [os.path.basename(x) for x in r_other]
		r_userdocs = [tuple(os.path.basename(x) for x in t) for t in r_userdocs]
		r_creatordocs = [tuple(os.path.basename(x) for x in t) for t in r_creatordocs]
		r_triplets = [tuple(os.path.basename(x) for x in t) for t in r_triplets]

	#Build a results object:
	deps_graph = {
		'depth':depth,
		'qvw':list(set(r_qvw)),
		'qvd':list(set(r_qvd)),
		'otherfiles':list(set(r_other)),
		'creatordocs':list(set(r_creatordocs)),
		'userdocs':list(set(r_userdocs)),
		'triplets':list(set(r_triplets))
	}
	
	return deps_graph #not interested in duplicates.

def generate_graphviz(deps_graph):
	"""Takes a logfile and returns a graphviz.it compatible graph of it's dependencies."""
	outputfile = 'depsgraph_graphviz.txt'
	# print('###')
	# for w in deps_graph['qvw']:
	# 	print(w[0],w[1])
	# print('###')

	output = ''
	output+=('digraph G {\n')
	output+=('layout="fdp";\n')
	index = {}
	#print(deps_graph['qvw'])
	for i, qvw in enumerate(deps_graph['qvw']):
		name = 'qvw' + str(i)
		index[qvw]=name
		if qvw is not 'None':
			output += '{0} [label="{1}",color="yellowgreen",shape=ellipse,style=filled]\n'.format(name,os.path.basename(qvw))
	for i, qvd in enumerate(deps_graph['qvd']):
		name = 'qvd' + str(i)
		index[qvd]=name
		output += '{0} [label="{1}",color="cornflowerblue",shape=rectangle,style=filled]\n'.format(name,os.path.basename(qvd))
	for i, f in enumerate(deps_graph['otherfiles']):
		name = 'other' + str(i)
		index[f]=name
		output += '{0} [label="{1}",color="slategray",shape=rectangle,style=filled]\n'.format(name,os.path.basename(f))
	#print(index)
	for x in deps_graph['triplets']:
		ia = index[x[0]]
		ib = index[x[1]]
		ic = index[x[2]]
		if x[2] == 'None':
			output += '{0} -> {1}\n'.format(ia,ib)
		elif x[0] == x[2]: #Circular reference.
			output += '{0} -> {1}\n'.format(ia,ib)
		else:
			output += '{0} -> {1} -> {2}\n'.format(ia,ib,ic)
	output += '}\n'

	return output
