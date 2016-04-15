"""Unit tests for regex expressions."""
import unittest, re, os
from qvstools.regex_store import *

tests_filesearch = [
	# These ones should return matches.
	(True,	r"this/is/a/path.qvd"),
	(True,	r"[this/is/a/path with spaces.qvd]"),
	(True,	r"[this/is/an/excel with spaces.xls]"),
	(True, 	r"FROM x.qvd (qvd);"),
	(True,	r"[this is a terrible-filename_qvd.qvd]"),
	(True,	r"[random csv file.csv]"),
	(True,	r"filename.with.extra.dots.qvd"),
	(True,	r"..\..\..\RelativePath1.qvd"),
	(True,	r"\\intranet.fake.com\this\is\a\unc\path.qvd"),
	(True,	r"[D:\path\with\drivename.xlsx]"),
	(True,	r"STORE mytable into mytable.qvd (qvd);"),
	#These ones should not:
	(False,	r"^fasf£$$"),
	(False,	r"[&dfas]"),
	(False,	r"This is just a sentence. Not sure how it would end up in a logfile but lets see.")
	#(False, r"ObviouslyAFile.qvd") # Will return true, should fail.
	##Needs more but this is a good start
]

tests_storeinto = [
	# These should return matches.
	(True,r"store Mytable into "),
	(True,r"STORE Mytable INTO "),
	(True,r"Store Mytable Into "),
	(True,r"Store [My Table] into "),
	(True,r"Store My_Table into "),
	(True,r"Store My-table into "),
	(True,r"Store My.Table into "),
	# These should not.
	(False,r"Store as Field_Store,")
]

tests_directory = [
	# These should return matches.
	(True,r"Directory ..\..\MyDir"),
	(True,r"DIRECTORY ..\..\MyDir"),
	# These should not.
	(False,r"thing as directory")
]

class TestRegex(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")
	
	def test_filesearch(self):
		print('Testing file search expression.')
		for x in tests_filesearch:
			if re.search(searches['filesearchstring2'],x[1]):
				result = True
			else:
				result = False
			try:
				self.assertEqual(result,x[0])
				print('{0}  >> {1} (correct)'.format(x[1],str(x[0])))
			except AssertionError:
				print('Failed on: {0} >> should return {1}'.format(x[1],str(x[0])))
				raise

	def test_storeinto(self):
		print('Testing store into search expression.')
		for x in tests_storeinto:
			if re.search(searches['store_statement'],x[1]):
				result = True
			else:
				result = False
			try:
				self.assertEqual(result,x[0])
				print('{0}  >> {1} (correct)'.format(x[1],str(x[0])))
			except AssertionError:
				print('Failed on: {0} >> should return {1}'.format(x[1],str(x[0])))
				raise

	def test_directorysearch(self):
		print('Testing directory search expression.')
		for x in tests_directory:
			if re.search(searches['directory_statement'],x[1]):
				result = True
			else:
				result = False
			try:
				self.assertEqual(result,x[0])
				print('{0}  >> {1} (correct)'.format(x[1],str(x[0])))
			except AssertionError:
				print('Failed on: {0} >> should return {1}'.format(x[1],str(x[0])))
				raise


if __name__ == '__main__':
        unittest.main()
