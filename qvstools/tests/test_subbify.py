import unittest, os, shutil
from qvstools.subbify import subbify

testdata_folder = os.path.join(os.path.dirname(__file__),'testdata')

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_subbify(self):
		print("Testing subbify")
		testinput = os.path.join(testdata_folder,'subbify_TestInput.qvs')
		print(testinput)
		subbify(testinput,open_after = False)
		##Cleanup
		shutil.rmtree(os.path.join(testdata_folder,'Subbify_TestInput_Subbified-prj'))
		os.remove(os.path.join(testdata_folder,'Subbify_TestInput_Subbified.qvw'))

if __name__ == '__main__':
	print(os.path.join(os.path.dirname(__file__),'testdata'))
	unittest.main()