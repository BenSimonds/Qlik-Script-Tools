import unittest, re, os
from qvstools.blocks import *

testdata_folder = os.path.join(os.path.dirname(__file__),'testdata')

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")
		#Delete output file:
		outputfiles = ['testoutput.txt','testoutput.xml']
		for x in outputfiles:
			try:
				os.remove(x)
			except FileNotFoundError:
				print('No file {0} to delete.'.format(x))

	def test_Block(self):
		print("Testing Block Class")
		goodblock = Block('good block','good description','good type','good text')
		self.assertEqual(goodblock.name, 'good block')
		self.assertEqual(goodblock.description,'good description')
		self.assertEqual(goodblock.type, 'good type')
		self.assertEqual(goodblock.text, 'good text')

	def test_BlockLibrary(self):
		print('Testing Block Library Class')
		#Create a block lib.
		myblocklib = BlockLibrary('Test')
		self.assertEqual(myblocklib.name,'Test')
		#Add a block from a text file.

		testblock_file = os.path.join(testdata_folder,'testblock_replacelist.qvs')

		myblocklib.add_text_block('Testblock','Test of Main block','BlockType',testblock_file)
		self.assertEqual(myblocklib.blocks['Testblock'].name,'Testblock')
		self.assertEqual(myblocklib.blocks['Testblock'].description, 'Test of Main block')
		self.assertEqual(myblocklib.blocks['Testblock'].type, 'BlockType')

		

		with open(testblock_file,'r') as comparetext:
			text_original = comparetext.read()
			text_scrubbed = '\n'.join([line for line in text_original.split('\n') if not re.search(r"//\(@[\d]",line) ]) 
			self.assertEqual(myblocklib.blocks['Testblock'].text,text_scrubbed)
		self.assertEqual(set(myblocklib.blocks['Testblock'].replacelist), set([('@0','Test Replace definition 0'),('@1','Test Replace definition 1'),('@2','Test Replace definition 2')]))

		with open(testblock_file,'r') as comparetext:
			text_original = comparetext.read()
			text_scrubbed = '\n'.join([line for line in text_original.split('\n') if not re.search(r"//\(@[\d]",line) ]) 

			self.assertEqual(myblocklib.blocks['Testblock'].text,text_scrubbed)
		#Test write a block
		myblocklib.blocks['Testblock'].write('testoutput.txt',['foo','bar','bad'])
		#Test string replacement.
		myblocklib.add_text_block('TestReplaceBlock','TestReplaceBlock','ReplaceType',testblock_file)
		myblocklib.blocks['TestReplaceBlock'].write('testoutput.txt',['a','b','c'])

	def test_writeTab(self):
		BlockLibrary.write_tab('TABNAME','testoutput.txt','w')	#Can call without instantiating because staticmethod. Yay!
		with open('testoutput.txt','r') as comparetext:
			self.assertEqual(comparetext.read(),'\n///$tab TABNAME\n')

	def test_QVD_write(self):
		print('Testing QVD load script writing.')
		#Load a qvd.
		tablename = 'Blah'

		testqvd_file = os.path.join(testdata_folder,'Test.qvd')

		testqvd = QVD(testqvd_file)
		#create a block library:
		myblocklib = BlockLibrary('Test')
		#Generate a block from my qvd.
		myblocklib.add_qvd_block(testqvd_file,'QVD_testqvd',tablename=tablename,prefix='XX')

		b1 = os.path.join(testdata_folder,'sub_Metadata.qvs')
		b2 = os.path.join(testdata_folder,'block_CallMeta.qvs')
		b3 = os.path.join(testdata_folder,'block_InitMeta.qvs')

		myblocklib.add_text_block('DEF_META','Meta SUB Definition','SUB',b1)
		myblocklib.add_text_block('CALL_META','Call meta block','BLOCK',b2)
		myblocklib.add_text_block('INIT_META','Initialise meta block','BLOCK',b3)

		myblocklib.blocks['DEF_META'].write('testoutput.txt',mode='w')
		myblocklib.blocks['INIT_META'].write('testoutput.txt')
		myblocklib.blocks['QVD_testqvd'].write('testoutput.txt')
		myblocklib.blocks['CALL_META'].write('testoutput.txt',[tablename])

	def test_add_directory_qvd(self):
		print('Testing loading a directory of qvds.')
		#create a block library:
		myblocklib = BlockLibrary('Test')
		#Load directory:
		myblocklib.add_directory_qvd(testdata_folder)
		#Write blocks to file.
		for block in [b for b in myblocklib.blocks if myblocklib.blocks[b].type == 'QVD']:
			myblocklib.blocks[block].write('testoutput.txt')

	def test_load_defaults(self):
		print('Testing loading the default blocks when creating a library.')
		myblocklib = BlockLibrary('Test',load_defaults = True)

	def test_xml_write(self):
		myblocklib = BlockLibrary('Test',load_defaults = True)
		for block in myblocklib.blocks:
			myblocklib.block_to_xml(block,directory='testoutput')

	def test_xml_read(self):
		myblocklib = BlockLibrary('Test')
		testblock_file = os.path.join(testdata_folder,'testblock_replacelist.qvs')
		myblocklib.add_text_block('testoutput','Block with replacelist.','BLOCK',testblock_file)
		#Copy block for comparison.
		myblocklib.blocks['A']=myblocklib.blocks['testoutput']
		#Write and read back (will overwrite):
		myblocklib.block_to_xml('testoutput',directory='.')
		myblocklib.add_xml_block('testoutput.xml')
		a = myblocklib.blocks['A']
		b = myblocklib.blocks['testoutput']
		self.assertEqual(a.type,b.type)
		self.assertEqual(a.text,b.text)
		self.assertEqual(a.description,b.description)
		self.assertEqual(a.replacelist,b.replacelist)


if __name__ == '__main__':
        unittest.main()
