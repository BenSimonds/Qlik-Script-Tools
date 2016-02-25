import unittest
from qvstools.blocks import Block, BlockLibrary, QVD

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDowm(self):
		print ("TEAR DOWN!")

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
		myblocklib.addtextblock('Testblock','Test of Main block','BlockType','blocks/source/tab_Main.qvs')
		self.assertEqual(myblocklib.blocks['Testblock'].name,'Testblock')
		self.assertEqual(myblocklib.blocks['Testblock'].description, 'Test of Main block')
		self.assertEqual(myblocklib.blocks['Testblock'].type, 'BlockType')
		self.assertEqual(myblocklib.blocks['Testblock'].text, open('blocks/source/tab_Main.qvs','r').read())
		self.assertEqual(set(myblocklib.blocks['Testblock'].replacelist), set([('@0','Test Replace definition 0'),('@1','Test Replace definition 1'),('@2','Test Replace definition 2')]))
		#Pickle that block.
		myblocklib.pickleblock('Testblock')
		#Remove it from the library.
		myblocklib.removeblock('Testblock')
		self.assertEqual(len(myblocklib.blocks.keys()),0)
		#Unpickle that block.
		myblocklib.addpickledblock('blocks/Testblock.p')
		#Test that block still has the same contents.
		self.assertEqual(myblocklib.blocks['Testblock'].text,open('blocks/source/tab_Main.qvs','r').read())
		#Test write a block
		myblocklib.writeblock('Testblock','test.qvs',['foo','bar','bad'])
		#Test string replacement.
		myblocklib.addtextblock('TestReplaceBlock','TestReplaceBlock','ReplaceType','blocks/source/block_CallMeta.qvs')
		myblocklib.writeblock('TestReplaceBlock','test2.qvs',['TestTableName'])


	def test_QVD(self):
		print('Testing QVD Class')
		#Load a qvd.
		testqvd = QVD('qvd/TestEmployees.qvd')

	def test_QVD_write(self):
		print('Testing QVD load script writing.')
		#Load a qvd.
		tablename = 'Blah'
		testqvd = QVD('qvd/TestEmployees.qvd',tablename=tablename,prefix='XX')
		#create a block library:
		myblocklib = BlockLibrary('Test')
		#Generate a block from my qvd.
		myblocklib.addqvdblock(testqvd)
		myblocklib.addtextblock('DEF_META','Meta SUB Definition','SUB','blocks/source/sub_Metadata.qvs')
		myblocklib.addtextblock('CALL_META','Call meta block','BLOCK','blocks/source/block_CallMeta.qvs')
		myblocklib.addtextblock('INIT_META','Initialise meta block','BLOCK','blocks/source/block_InitMeta.qvs')

		myblocklib.writeblock('DEF_META','test3.qvs',[],'w')
		myblocklib.writeblock('INIT_META','test3.qvs',[])
		myblocklib.writeblock('QVD_' + tablename,'test3.qvs',[])
		myblocklib.writeblock('CALL_META','test3.qvs',[tablename])

if __name__ == '__main__':
        unittest.main()
