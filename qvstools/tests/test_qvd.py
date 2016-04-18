import unittest, re, os
from qvstools.blocks import *

testdata_folder = os.path.join(os.path.dirname(__file__),'testdata')


class TestQVD(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")

	def test_QVD(self):
		print('Testing QVD Class')
		#Load a qvd.
		qvd_file = os.path.join(testdata_folder,'Test.qvd')
		testqvd = QVD(qvd_file)


if __name__ == '__main__':
        unittest.main()
