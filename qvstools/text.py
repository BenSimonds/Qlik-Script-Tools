"""Tools for helping with text files, encodings etc."""
import re
import sys
import os


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
	"""Uses :func:`detect_encoding <qvstools.text.detect_encoding>` to get encoding and returns a unicode string of the text file"""
	encoding  = detect_encoding(textfile)
	with open(textfile,'r',encoding=encoding,errors='replace') as f:
		fulltext = f.read()
		return fulltext