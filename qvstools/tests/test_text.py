import unittest, re, os
from qvstools.text import *

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_detect_encoding(self):
		paths = [
			r"qvstools\tests\testdata\ETLTubeData_Subbified.qvw.log",
			r"qvstools\tests\testdata\Subbify_TestInput.qvs",
			r"qvstools\tests\testdata\ETLTubeData.qvs",
			r"qvstools\tests\testdata\TestPRJ-prj\LoadScript.txt",
			r"qvstools\tests\testdata\TestPRJ-prj\SH01.xml"
			]

		for path in paths:
			result = detect_encoding(path)
			#print(result)
			with open(path,'r',encoding=result) as f:
				#print(f.read(50))
				pass

if __name__ == '__main__':
        unittest.main()

