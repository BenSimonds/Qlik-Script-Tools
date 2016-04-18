import unittest, re, os
from qvstools.prj import *
import xml.etree.ElementTree as ET

testdata_folder = os.path.join(os.path.dirname(__file__),'testdata')

class TestPRJ(unittest.TestCase):
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

	def test_prj_class(self):
		print('Testing PRJ class.')
		folder = os.path.join(testdata_folder,'TestPRJ-prj')
		prj = PRJ(folder)
		self.assertEqual('TestPRJ',prj.name)
		self.assertEqual(folder,prj.path)
		self.assertEqual(len(os.listdir(folder)),len(prj.all_files))

	def test_object (self):
		path = os.path.join(testdata_folder,'TestPRJ-prj/TX01.xml')
		obj = QVObject(path)
		self.assertEqual('TX01',obj.id)
		self.assertEqual(obj.path,path)
		obj.write(path='testoutput.txt')
		with open(path,'r') as original_file:
			original = original_file.read()#.replace('\r\n','\n')
			with open('testoutput.txt','r') as written_file:
				written = written_file.read()
				self.assertEqual(original,written)

	def test_prj_findreplace(self):
		folder = os.path.join(testdata_folder,'TestPRJ-prj')
		prj = PRJ(folder)
		prj.find_replace_elements(".//FontName",'Calibri')			

	def test_rescale(self):
		folder = os.path.join(testdata_folder,'TestPRJ-prj')
		prj = PRJ(folder)
		prj.rescale_layout(1920,1080,global_rescale=True)

if __name__ == '__main__':
	print(os.path.join(os.path.dirname(__file__),'testdata'))
	unittest.main()

