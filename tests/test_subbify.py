import unittest, os
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
		subbify(testinput)

