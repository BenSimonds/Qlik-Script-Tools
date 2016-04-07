import unittest, re, os
from qvstools.text import *

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_detect_encoding(self):
		paths = [
			r"testdata\ETLTubeData_Subbified.qvw.log",
			r"testdata\Subbify_TestInput.qvs",
			r"testdata\ETLTubeData.qvs",
			r"testdata\TestPRJ-prj\LoadScript.txt",
			r"testdata\TestPRJ-prj\SH01.xml"
			]

		for path in paths:
			result = detect_encoding(path)
			#print(result)
			with open(path,'r',encoding=result) as f:
				#print(f.read(50))
				pass

	def test_parse_logfile(self):
		print('Testing logfile parse.')
		log = r"testdata\ETLTubeData_Subbified.qvw.log"
		
		lf = LogFile(log)

		for f in lf.get_files_touched():
			print(f,lf.find_file(f))

if __name__ == '__main__':
        unittest.main()

