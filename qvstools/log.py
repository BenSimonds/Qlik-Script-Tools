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
		"""Tag lines that reference qvds or other files within the logfile."""

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
		print('\nParsed!')
		return matchlines

	def get_file_lines(self):
		"""returns a list of the files found by tag_file_lines"""
		files_touched = [line for line in self.lines if 'file' in line.keys()]
		return files_touched

	def find_file(self,line):
		"""Checks if the file exists and returns its absolute path."""
		
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


def build_dependency_graph(path,depth=100):
	"""Recursively looks through log files to build a dependency graph.

	Steps:
		1. Start with the logfile, and find all the files it generates.
		2. For the qvd files, find the creator doc for those files, and see if *that* file has a logfile.
		3. If it does, see step 1.
		.
		.
		N. Once all your logfiles have been searched through, write out the dependency chain in some handy format.
	"""

	def gather_deps(logfile_input):
		"""Returns a tuple for each dependency: (qvw_loaded_by,file_loaded,qvd_created_by)"""
		if not os.path.isfile(logfile_input):
			print('Could not find logfile: {0}'.format(logfile_input))
			return None
		else:
			qvw = logfile_input[0:-4]
			lf = LogFile(logfile_input)
			deps = []
			for l in lf.get_file_lines():
				file = lf.find_file(l)
				if file:
					if file.endswith('.qvd'):
						creatordoc = QVD(file).CreatorDoc
					else:
						creatordoc = None
				else:
					file = l['file'] + '(UNFOUND)'
					creatordoc = None
				deps.append((qvw,file,creatordoc))
			return deps

	input_error_message = 'This function takes a logfile or a qvw file (that has a log file associated with it). Did you supply a valid qvw or log file?'
	#Sense check inut:
	if path.endswith('.log'):
		if os.path.isfile(path):
			logfile_input = path
		else:
			print(input_error_message,'NOT LOG')
			return
	elif path.endswith('.qvw'):
		if os.path.isfile(path):
			logfile_input = path + '.log'
		else:
			print(input_error_message,'NOT QVW')
			return
	else:
		print(input_error_message,'NEITHER')
		return

	deps_all = []
	counter  = 0
	logfiles_working = [logfile_input]
	logfiles_done = []

	while counter < depth and len(logfiles_working) > 0:
		for l in logfiles_working:
			deps = gather_deps(l)
			deps_all += deps
			logfiles_done = list(set(logfiles_done + logfiles_working))
			logfiles_working = list(set([x[2]+'.log' for x in deps if x[2] and x[2]+'.log' not in logfiles_done]))

	return list(set(deps_all)) #not interested in duplicates.





	


