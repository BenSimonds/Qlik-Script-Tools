import unittest, re, os, json
from qvstools.log import *
from qvstools.text import known_encodings

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")
		#Delete output file:
		outputfiles = ['testoutput.txt']
		try:
			delete = [os.remove(x) for x in outputfiles]
		except FileNotFoundError:
			print('No files to delete.')

	def test_detect_encoding(self):
		paths = [
			r"qvstools\tests\testdata\ETLTubeData_Subbified.qvw.log",
			r"qvstools\tests\testdata\Subbify_TestInput.qvs",
			r"qvstools\tests\testdata\ETLTubeData.qvs",
			r"qvstools\tests\testdata\TestPRJ-prj\LoadScript.txt",
			r"qvstools\tests\testdata\TestPRJ-prj\SH01.xml"
			]

		for path in paths:
			result = detect_log_encoding(path,known_encodings['log'])
			#print(result)
			with open(path,'r',encoding=result) as f:
				#print(f.read(50))
				pass


	def test_parse_logfile(self):
		print('Testing logfile parse.')
		logs = [
			r"qvstools\tests\testdata\DepsGraph1.qvw.log",
			r"qvstools\tests\testdata\DepsGraph2.qvw.log",
			r"qvstools\tests\testdata\DepsGraph3.qvw.log",
			r"qvstools\tests\testdata\ETLTubeData_Subbified.qvw.log"
			]
		
		for log in logs:
			lf = LogFile(log)

			for f in lf.get_file_lines():
				print(f['file'],' --> ',lf.find_file(f))

	def test_parse_logfile_remap(self):
		print('Testing logfile parse with path remapping.')
		log = r"qvstools\tests\testdata\ETLTubeData_Subbified.qvw.log"
		lf = LogFile(log)
		for f in lf.get_file_lines():
			print(f['file'],' --> ',lf.find_file(f))

	def test_build_dependency_graph(self):
		test_input = r"qvstools\tests\testdata\DepsGraph3.qvw"
		with open('testoutput_deps_graph','w') as f:
			json.dump(build_dependency_graph(test_input,depth=100),f,sort_keys=True,indent=4, separators=(',', ': '))
		

	def test_generate_graphviz(self):
		test_input = r"qvstools\tests\testdata\DepsGraph3.qvw"
		with open('testoutput_graphviz','w') as f:
			f.write(generate_graphviz(build_dependency_graph(test_input,depth=100)))

if __name__ == '__main__':
        unittest.main()

