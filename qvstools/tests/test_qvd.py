import unittest, re, os
from qvstools.blocks import *

class TestQVD(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_QVD(self):
		print('Testing QVD Class')
		#Load a qvd.
		testqvd = QVD(r'qvstools\tests\testdata\Test.qvd')


if __name__ == '__main__':
        unittest.main()
