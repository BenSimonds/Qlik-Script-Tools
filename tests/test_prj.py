import unittest, re
from qvstools.prj import *
import xml.etree.ElementTree as ET

class TestPRJ(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDowm(self):
		print ("TEAR DOWN!")

	def test_prj_class(self):
		print('Testing PRJ class.')
		folder = 'QVW/TestPRJ-prj'
		prj = PRJ(folder)
		self.assertEqual('TestPRJ',prj.name)
		self.assertEqual(folder,prj.path)
		self.assertEqual(len(os.listdir(folder)),len(prj.all_files))

	def test_object (self):
		path = 'QVW/TestPRJ-prj/TX01.xml'
		obj = QVObject(path)
		self.assertEqual('TX01',obj.id)
		self.assertEqual(obj.path,path)
		obj.write(path='testoutput_textobject.xml')
		with open(path,'rb') as original_file:
			original = original_file.read()
			with open('testoutput_textobject.xml','rb') as written_file:
				written = written_file.read()
				self.assertEqual(original,written)

	def test_prj_findreplace(self):
		folder = 'QVW/TestPRJ-prj'
		prj = PRJ(folder)
		prj.find_replace_elements(".//FontName",'Calibri')			