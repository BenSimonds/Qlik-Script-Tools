"""Tools for reading logfiles and working out dependencies."""
import re
import sys
import os
from qvstools.qvd import QVD
from qvstools.regex_store import searches
from qvstools.text import detect_encoding, decode_with_detected

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
		fulltext = decode_with_detected(textfile)
		parsed = []
		lines = fulltext.split('\n')
		for l in lines:
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
		#Tag lines that reference qvds or other files within the logfile.

		filesearch = searches['filesearchstring2']	#Finds a qvd. Returns the name in the capture group.
		storesearch = searches['store_statement']
		dirsearch = searches['directory_statement']
		
		matchlines = []
		optype = 'LOAD'	#By default expect matches to be load statements.
		workingdir = self.dir
		no_of_lines = len(self.lines)
		for line in range(0,no_of_lines - 1):
			#print('Parsing line {0} of {1}'.format(line,no_of_lines),end='')
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
		print('Parsed!')
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


def build_dependency_graph(path,depth=3,maxfiles=100):
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
		'qvw': [list of tuples (basename,abspath) for each qvw logfile scanned or named as a creatordoc],
		'qvd': [list of tuples (basename,abspath) for each qvd file found],
		'otherfiles': [list of tuples (basename,abspath) for each non qvd data file found]
		'creatordocs': [list of tuples (qvd_basename,qvd_abspath,creatordoc_basename,creatordoc_abspath) for each qvd file found],
		'userdocs':[list of tuples (userdoc_basename,userdoc_abspath,qvd_basename,qvd_abspath) for each qvd file found],
		'triplets':[list of tuples (userdoc_basename,userdoc_abspath,qvd_basename,qvd_abspathcreatordoc_basename,creatordoc_abspath) for each qvd file found]
		}
		
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
			for l in lf.get_file_lines():
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
			return deps

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
	r_qvd = [] 		# QVDs (basename,abspath)
	r_qvw = [] 	# QVWs (basename,abspath)
	r_other = [] 	# Other files (excel,csv) (basename,abspath)
	r_creatordocs = [] # List of tuples: (qvd basename, qvd abspath,creatordoc basename, creatodoc abspath) 
	r_userdocs = [] #List of tuples (qvw basename, qvw abspath,file basename, file abspath)
	r_triplets = [] #List of tuples (userdoc basename, userdoc abspath,file basename, file abspath,creatordoc basename, creatordoc abspath)

	while counter_depth < depth and counter_files < maxfiles and len(logfiles_working) > 0:
		counter_depth += 1
		# Pop a logfile from the list to work on.
		l = logfiles_working.pop()

		#Append it to logfiles_done so it won't get done again.
		logfiles_done.append(l)

		#Add the associated qvw to our results.
		qvw_current = l[0:-4]
		r_qvw.append((os.path.basename(qvw_current),qvw_current))

		#Gather deps on it if we haven't reached maxfiles:
		if counter_files < maxfiles:
			counter_files += 1
			deps = gather_deps(l)
			#If it has any add them to our results.
			if deps:
				# Add the deps triplets to the results.
				r_qvd += [(os.path.basename(d[1]) , d[1]) for d in deps if d[1].endswith('.qvd')]
				r_other += [(os.path.basename(d[1]) , d[1]) for d in deps if not d[1].endswith('.qvd')]
				r_userdocs += [
					(
					os.path.basename(d[0]), d[0],
					os.path.basename(d[1]), d[1]
					) 
					for d in deps]
				r_creatordocs += [
					(
					os.path.basename(d[1]), d[1],
					os.path.basename(d[2]), d[2]
					)
					for d in deps]
				r_triplets += [
					(
					os.path.basename(d[0]), d[0],
					os.path.basename(d[1]), d[1],
					os.path.basename(d[2]), d[2]
					)
					for d in deps]
				r_qvw += [(os.path.basename(d[2]),d[2]) for d in deps if (os.path.basename(d[2]),d[2]) not in r_qvw]

				#Add any new creatordocs to logfiles_working.
				for d in deps:
					dlog = d[2]+'.log'
					if dlog not in logfiles_done + logfiles_working:
						logfiles_working.append(dlog)
		else:
			break

	#Build a results object:
	deps_graph = {
		'depth':depth,
		'maxfiles':maxfiles,
		'qvw':list(set(r_qvw)),
		'qvd':list(set(r_qvd)),
		'otherfiles':list(set(r_other)),
		'creatordocs':list(set(r_creatordocs)),
		'userdocs':list(set(r_userdocs)),
		'triplets':list(set(r_triplets))
	}
	
	return deps_graph #not interested in duplicates.

def generate_graphviz(path,depth=4,maxfiles=100):
	"""Takes a logfile and builds a graphviz.it compatible graph of it's dependencies."""
	outputfile = 'depsgraph_graphviz.txt'
	deps = build_dependency_graph(path,depth=depth,maxfiles=maxfiles)
	print('###')
	for w in deps['qvw']:
		print(w[0],w[1])
	print('###')

	with open(outputfile,'w') as output:
		output.write('digraph G {\n')
		index = {}
		for i, qvw in enumerate(deps['qvw']):
			name ='qvw' + str(i)
			index[qvw[1]]=name
			output.write('{0} [label="{1}",color="yellowgreen",shape=ellipse,style=filled]\n'.format(name,qvw[0]))
		for i, qvd in enumerate(deps['qvd']):
			name = 'qvd' + str(i)
			index[qvd[1]]=name
			output.write('{0} [label="{1}",color="cornflowerblue",shape=rectangle,style=filled]\n'.format(name,qvd[0]))
		for i, f in enumerate(deps['otherfiles']):
			name = 'other' + str(i)
			index[f[1]]=name
			output.write('{0} [label="{1}",color="slategray",shape=rectangle],style=filled\n'.format(name,f[0]))
		print(index)
		for x in deps['triplets']:
			ia = index[x[1]]
			ib = index[x[3]]
			ic = index[x[5]]
			output.write('{0} -> {1} -> {2}\n'.format(ia,ib,ic))
		output.write('}\n')