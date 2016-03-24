"""Tools for helping with text files, encodings etc."""

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

def parse_logfile(textfile):
	encoding = detect_encoding(textfile)
	parsed = []
	limit = 200
	with open(textfile,'r',encoding=encoding) as f:
		#Start looping through lines.
		lines = f.readlines()
		for l in lines[0:limit]:
			#First 10 chars are the date:
			date = l[0:10]
			#Gap of 1 char, then next 8 are time.
			time = l[11:19]
			#22-26  are operation no:
			op = l[21:25]
			#the rest is unknown...
			rest = l[26:].strip()
			lp = (date,time,op,rest)
			parsed.append(lp)
	return parsed
