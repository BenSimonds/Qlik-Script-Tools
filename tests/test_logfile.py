import unittest, re, os
from qvstools.log import *

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_parse_logfile(self):
		print('Testing logfile parse.')
		logs = [
			r"testdata\DepsGraph1.qvw.log",
			r"testdata\DepsGraph2.qvw.log",
			r"testdata\DepsGraph3.qvw.log",
			r"testdata\ETLTubeData_Subbified.qvw.log"
			]
		
		for log in logs:
			lf = LogFile(log)

			for f in lf.get_file_lines():
				print(f['file'],' --> ',lf.find_file(f))

	def test_build_dependency_graph(self):
		test_input = r"testdata\DepsGraph3.qvw"
		deps = build_dependency_graph(test_input)
		for x in deps:
			print([os.path.basename(y) for y in x if y])


if __name__ == '__main__':
        unittest.main()

