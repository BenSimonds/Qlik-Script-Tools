import unittest, re, os
from qvstools.text import *

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_detect_encoding(self):
		paths = [
			r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\testdata\ETLTubeData_Subbified.qvw.log",
			r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\testdata\Subbify_TestInput.qvs",
			r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\testdata\ETLTubeData.qvs",
			r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\testdata\TestPRJ-prj\LoadScript.txt",
			r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\testdata\TestPRJ-prj\SH01.xml"
			]

		for path in paths:
			result = detect_encoding(path)
			#print(result)
			with open(path,'r',encoding=result) as f:
				#print(f.read(50))
				pass

	def test_parse_logfile(self):
		print('Testing logfile parse.')
		log = r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\testdata\ETLTubeData_Subbified.qvw.log"
		
		lf = LogFile(log)

if __name__ == '__main__':
        unittest.main()

