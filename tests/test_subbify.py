import unittest, os, shutil
from qvstools.subbify import subbify

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_subbify(self):
		print("Testing subbify")
		testinput = 'testdata\\Subbify_TestInput.qvs'
		print(testinput)
		subbify(testinput,open_after = False)
		##Cleanup
		shutil.rmtree('testdata\\Subbify_TestInput_Subbified-prj')
		os.remove('testdata\\Subbify_TestInput_Subbified.qvw')

