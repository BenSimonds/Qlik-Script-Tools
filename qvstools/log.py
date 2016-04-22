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

	def parse_logfile(self, textfile):
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

		# File search stuff:
		working_dir = self.dir
		filesearch = searches['filesearchstring2']	#Finds a qvd. Returns the name in the capture group.
		storesearch = searches['store_statement']
		dirsearch = searches['directory_statement']
		optype = 'LOAD'	#By default expect matches to be load statements.
		
		for l in lines:
			### First the basic stuff:
			#First 10 chars are the date:
			date = l[0:10]

			#Gap of 1 char, then next 8 are time.
			time = l[11:19]

			#22-26  are operation no:
			op = l[21:25]

			#the rest is unknown...
			rest_of_line = l[26:].strip()

			### Now search for files as well
			#Keep an eye out for store statements, these precede stored files.
			if re.search(storesearch,rest_of_line):
				optype = 'STORE'

			#Also for directory statements, these change where files are searched for in relative paths.
			if rest_of_line.strip().upper().startswith('DIRECTORY'):
				working_dir = rest_of_line[10:].strip()

			#Now do the search:
			s = re.search(filesearch,rest_of_line)
			file_referenced	= False
			file_path = None
			file_op_type = None
			file_found = False
			file_abspath = None
			file_basename = None

			if s and isinstance(s.group(1),str) and isinstance(s.group(2),str):
				file_path = s.group(1) + '.' + s.group(2)
			elif s and isinstance(s.group(3),str) and isinstance(s.group(4),str):
				file_path = s.group(3) + '.' + s.group(4)
			if file_path:
				file_referenced = True 
				file_path = file_path.replace('\\\\','\\')
				file_op_type = optype
				
				#Look for file to see if it exists:
				file_found = self.find_file(file_path,working_dir) is not None
				file_abspath = self.find_file(file_path,working_dir)
				if file_found:
					file_basename = os.path.basename(self.find_file(file_path,working_dir))
				else:
					file_basename = None

				#reset optype
				optype = 'LOAD'

			lp = {
				'date':date,
				'time':time,
				'op':op,
				'text':rest_of_line,
				'working_dir':working_dir,
				'file_referenced':file_referenced,
				'file_path_original':file_path,
				'file_found': file_found,
				'file_abspath': file_abspath,
				'file_basename': file_basename,
				'file_op_type':file_op_type
				}

			parsed.append(lp)
		return parsed

	def get_file_lines(self):
		"""Returns a list of the files found by tag_file_lines."""
		files_touched = [line for line in self.lines if line['file_referenced']]
		return files_touched

	def find_file(self,path,working_dir):
		#Checks if the file exists and returns its absolute path.
		if path is None:
			return None		
		f = path
		wd = working_dir
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
			joined_basename = os.path.basename(joined)
			if os.path.isfile(joined):
				return joined
			else:
				return None


def build_dependency_graph(path,depth=100,remap_paths=False,basenames_only=False,blacklist=[]):
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
	:param basenames_only: Output will filepaths will be given as basenamees only.
	:param blacklist: A list of logfiles not to touch. can use wildcard * to blacklist any files beginning with that string. Otherwise should end in '.qvw.log'.

	"""
	### Sub functions that get repeated ###
	def gather_deps(logfile_input):
		"""Returns a tuple for each dependency: (qvw_loaded_by,file_loaded,qvd_created_by)"""
		#Check for a valid logfile:
		if not os.path.isfile(logfile_input):
			print('Could not find logfile: {0}'.format(logfile_input))
			return None
		else:
			#  Gather data and set up
			qvw = logfile_input[0:-4]
			lf = LogFile(logfile_input)
			deps = []

		
			for l in lf.get_file_lines():
				# Populate base triplet as a list to make it easy to assign to.
				deps_triplet = [qvw,'None','None']
				
				if l['file_found']:
					l_file = l['file_abspath']
					deps_triplet[1] = l_file
					if l_file.endswith('.qvd'):
						creatordoc = QVD(l_file).CreatorDoc
						deps_triplet[2] = creatordoc
					else:
						pass
				else:
					deps_triplet[1] = l['file'] + '(unfound)'

				deps_triplet = tuple(deps_triplet) #Convert to tuple so that silly things can't happen to it.
				deps.append(deps_triplet)
			
			#Print some handy output:
			qvds = set([x[1] for x in deps])
			creatordocs = set([x[2] for x in deps])
			print('{0} Creator Docs Found:'.format(len(creatordocs)))
			for x in creatordocs:
				print(x)
			print('{0} Data Files Found:'.format(len(qvds)))
			for x in qvds:
				print(x)
			return deps

	def remap_path(abspath):
		if remap_paths:
			for key, value in remap_paths.items():
				if abspath.startswith(key):
					return value + abspath[len(key):]
		return abspath

	def is_blacklisted(abspath):
		if abspath in blacklist:
			return True
		else:
			for b in [b[0:-1] for b in blacklist if b.endswith('*')]:
				if abspath.startswith(b):
					return True
		return False

	### Function Proper Starts Here ###
	input_error_message = 'This function takes a logfile or a qvw file (that has a log file associated with it). Did you supply a valid qvw or log file?'

	#Sense check inut:
	if path.endswith('.log'):
		if os.path.isfile(path):
			logfile_input = os.path.abspath(path)
			root_qvw = os.path.abspath(path[0:-4] + '.qvw')
		else:
			print(input_error_message,'NO LOG FOUND')
			return
	elif path.endswith('.qvw'):
		if os.path.isfile(path):
			logfile_input = os.path.abspath(path + '.log')
			root_qvw = os.path.abspath(path)
		else:
			print(input_error_message,'NO QVW FOUND')
			return
	else:
		print(input_error_message,'INVALID / NO FILE')
		return

	# Set up vars:
	deps_all = []
	counter_depth  = 0
	logfiles_working = [logfile_input] #Starts with just the input logfile, will grow as creatordocs are found.
	logfiles_done = [] #Starts empty, grows when a logfile is processed.

	##Results objects:
	r_qvd = [] 			# QVDs (abspath)
	r_qvw = [] 			# QVWs (abspath)
	r_other = [] 		# Other files (excel,csv) (abspath)
	r_creatordocs = [] 	# List of tuples: (qvd,creatodoc) 
	r_userdocs = [] 	#List of tuples (qvw,file )
	r_triplets = [] 	#List of tuples (userdoc,file,creatordoc)

	while counter_depth < depth and len(logfiles_working) > 0:
		counter_depth += 1

		# Pop a logfile from the list to work on.
		l = logfiles_working.pop()
		print('\n\nGathering deps for {0}'.format(l))

		# Append it to logfiles_done so it won't get done again.
		logfiles_done.append(l)

		# Add the associated qvw to our results.
		qvw_current = l[0:-4]
		r_qvw.append(qvw_current)

		# Gather deps on it.
		deps = gather_deps(l)

		# Remap paths if required.
		if remap_paths and deps:
			deps = [tuple(remap_path(x) for x in d) for d in deps]
			
		#If it has any dependencies add them to our results.
		if deps:
			# These ones are lists of strings:
			r_qvd 	+= [d[1] for d in deps if d[1].endswith('.qvd')]
			r_other += [d[1] for d in deps if not d[1].endswith('.qvd')]
			r_qvw 	+= [d[2] for d in deps if d[2] not in r_qvw]

			# These ones are lists of tuples.
			r_userdocs 		+= [(d[0],d[1]) for d in deps]
			r_creatordocs 	+= [(d[1],d[2]) for d in deps]
			r_triplets 		+= [(d[0], d[1], d[2]) for d in deps]
			
			#Add any new creatordocs to logfiles_working.
			for d in deps:
				dlog = d[2]+'.log'
				if dlog not in logfiles_done and dlog not in logfiles_working and not is_blacklisted(dlog):
					if  os.path.isfile(dlog):
						logfiles_working.append(dlog)
					else:
						print('Missing/Blacklisted Logfile: {0}'.format(dlog))
						logfiles_working.append(dlog)

		print('Finished with {0}'.format(l))
		# print('Still to do:')
		# for f in logfiles_working:
		# 	print(f)
		

	if basenames_only:
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
	"""Takes a logfile and returns a graphviz.it compatible graph of it's dependencies.
	
	A better structure for this graph can be found at http://graphviz.it/#/gallery/tree.gv"""
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
