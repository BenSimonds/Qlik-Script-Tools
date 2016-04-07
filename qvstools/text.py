"""Tools for helping with text files, encodings etc."""
import re
import sys
import os
from qvstools.regex_store import searches

def detect_encoding(textfile):
	"""Tries to open textfile with a variety of encodings and returns the one that works"""

	encodings = [
		'utf-8-sig',
		'utf-16',
		'utf-8',
		'UTF-16LE',
		'cp1252',
		'cp1251'
		]

	with open(textfile,'rb') as f:
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

def decode_with_detected(textfile):
	"""Uses detect_encoding to get encoding and returns a unicode string of the text file"""
	encoding  = detect_encoding(textfile)
	with open(textfile,'r',encoding=encoding,errors='replace') as f:
		fulltext = f.read()
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
			sys.stdout.write('\rParsing line {0} of {1}'.format(line,no_of_lines))
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

	def get_files_touched(self):
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
