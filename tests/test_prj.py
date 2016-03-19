import unittest, re
from qvstools.prj import *
import xml.etree.ElementTree as ET

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
		folder = 'testdata/TestPRJ-prj'
		prj = PRJ(folder)
		self.assertEqual('TestPRJ',prj.name)
		self.assertEqual(folder,prj.path)
		self.assertEqual(len(os.listdir(folder)),len(prj.all_files))

	def test_object (self):
		path = 'testdata/TestPRJ-prj/TX01.xml'
		obj = QVObject(path)
		self.assertEqual('TX01',obj.id)
		self.assertEqual(obj.path,path)
		obj.write(path='testoutput.txt')
		with open(path,'rb') as original_file:
			original = original_file.read()
			with open('testoutput.txt','rb') as written_file:
				written = written_file.read()
				self.assertEqual(original,written)

	def test_prj_findreplace(self):
		folder = 'testdata/TestPRJ-prj'
		prj = PRJ(folder)
		prj.find_replace_elements(".//FontName",'Calibri')			