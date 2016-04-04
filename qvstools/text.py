"""Tools for helping with text files, encodings etc."""
import re
import sys

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


class LogFile:
	"""Parses a qlikview logfile and creates an object with it's info more easliy accessible."""
	def __init__(self,textfile):
		"""Take a Logfile and turn it into an object."""
		self.path = textfile
		self.lines = self.parse_logfile(textfile)
		self.tag_file_lines()


	@staticmethod
	def parse_logfile(textfile):
		encoding = detect_encoding(textfile)
		parsed = []
		with open(textfile,'r',encoding=encoding) as f:
			#Start looping through lines.
			lines = f.readlines()
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
		filesearchstring = r"(?:\s|\[|^)((?:\.\.|\\\\|\\)?[\\\w \-_]+)\.(qvd|xls[xm]?)\]?"
		storesearchstring = r"store\s\[?[\w\s]*\]?\sinto"

		filesearch = re.compile(filesearchstring)	#Finds a qvd. Returns the name in the capture group.
		storesearch = re.compile(storesearchstring)
		
		matchlines = []
		optype = 'LOAD'	#By default expect matches to be load statements.
		no_of_lines = len(self.lines)
		for line in range(0,no_of_lines - 1):
			sys.stdout.write('\rParsing line {0} of {1}'.format(line,no_of_lines))
			linetext = self.lines[line]['text']
			if re.search(storesearch,linetext):
				optype = 'STORE'
			s = re.search(filesearch,linetext)
			if s:
				file = s.group(1) + '.' + s.group(2)
				self.lines[line]['file'] = file
				self.lines[line]['load'] = optype == 'LOAD'
				self.lines[line]['store'] = optype == 'STORE'
				matchlines.append(file)
			#reset optype
				optype = 'LOAD'
		print('\nParsed!')
		return matchlines
