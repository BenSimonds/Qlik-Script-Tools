import unittest, re, os, json
from qvstools.log import *
from qvstools.text import known_encodings

testdata_folder = os.path.join(os.path.dirname(__file__),'testdata')

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")
		#Delete output file:
		# outputfiles = ['testoutput.txt','testoutput_deps_graph.txt','testoutput_graphviz.txt']
		# for x in outputfiles:
		# 	try:
		# 		os.remove(x)
		# 	except FileNotFoundError:
		# 		print('No files to delete.')

	def test_detect_encoding(self):
		test_files = [
			(os.path.join(testdata_folder,"ETLTubeData_Subbified.qvw.log"),'log')
			]

		for t in test_files:
			result = detect_log_encoding(t[0],known_encodings[t[1]])
			#print(result)
			with open(t[0],'r',encoding=result) as f:
				#print(f.read(50))
				pass


	def test_parse_logfile(self):
		print('Testing logfile parse.')
		logs = [
			os.path.join(testdata_folder,"DepsGraph1.qvw.log"),
			os.path.join(testdata_folder,"DepsGraph2.qvw.log"),
			os.path.join(testdata_folder,"DepsGraph3.qvw.log"),
			os.path.join(testdata_folder,"ETLTubeData_Subbified.qvw.log")
			]
		
		for log in logs:
			lf = LogFile(log)

			for f in lf.get_file_lines():
				print(f['file_referenced'],' --> ',f['file_abspath'])

	def test_parse_logfile_remap(self):
		print('Testing logfile parse with path remapping.')
		log = os.path.join(testdata_folder,"ETLTubeData_Subbified.qvw.log")
		lf = LogFile(log)
		for f in lf.get_file_lines():
			print(f['file_referenced'],' --> ',f['file_abspath'])

	def test_build_dependency_graph(self):
		test_input = os.path.join(testdata_folder,"DepsGraph3.qvw")
		with open('testoutput_deps_graph.txt','w') as f:
			json.dump(build_dependency_graph(test_input,depth=100),f,sort_keys=True,indent=4, separators=(',', ': '))
		

	def test_generate_graphviz(self):
		test_input = os.path.join(testdata_folder,"DepsGraph3.qvw")
		with open('testoutput_graphviz.txt','w') as f:
			f.write(generate_graphviz(build_dependency_graph(test_input,depth=100,basenames_only=True),style=2))

if __name__ == '__main__':
        unittest.main()

