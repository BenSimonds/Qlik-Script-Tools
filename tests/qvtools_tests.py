try:
	from nose.tools import *
except ImportError:
	pass
from qvstools.blocks import Block, BlockLibrary, QVD

def setup():
	print ("SETUP!")

def teardown():
	print ("TEAR DOWN!")

# def test_basic():
# 	print("I RAN!")	

def test_Block():
	print("Testing Block Class")
	goodblock = Block('good block','good description','good type','good text')
	assert_equal(goodblock.name, 'good block')
	assert_equal(goodblock.description,'good description')
	assert_equal(goodblock.type, 'good type')
	assert_equal(goodblock.text, 'good text')

def test_BlockLibrary():
	print('Testing Block Library Class')
	#Create a block lib.
	myblocklib = BlockLibrary('Test')
	assert_equal(myblocklib.name,'Test')
	#Add a block from a text file.
	myblocklib.addtextblock('Testblock','Test of Main block','BlockType','blocks/source/tab_Main.qvs')
	assert_equal(myblocklib.blocks['Testblock'].name,'Testblock')
	assert_equal(myblocklib.blocks['Testblock'].description, 'Test of Main block')
	assert_equal(myblocklib.blocks['Testblock'].type, 'BlockType')
	assert_equal(myblocklib.blocks['Testblock'].text, open('blocks/source/tab_Main.qvs','r').read())
	#Pickle that block.
	myblocklib.pickleblock('Testblock')
	#Remove it from the library.
	myblocklib.removeblock('Testblock')
	assert_equal(len(myblocklib.blocks.keys()),0)
	#Unpickle that block.
	myblocklib.addpickledblock('Testblock')
	#Test that block still has the same contents.
	assert_equal(myblocklib.blocks['Testblock'].text,open('blocks/source/tab_Main.qvs','r').read())
	#Test write a block
	myblocklib.writeblock('Testblock','test.qvs',[])
	#Test string replacement.
	myblocklib.addtextblock('TestReplaceBlock','TestReplaceBlock','ReplaceType','blocks/source/block_CallMeta.qvs')
	myblocklib.writeblock('TestReplaceBlock','test2.qvs',['TestTableName'])


def test_QVD():
	print('Testing QVD Class')
	#Load a qvd.
	testqvd = QVD('qvd/TestEmployees.qvd')

def test_QVD_write():
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
	myblocklib.writeblock('INIT_META','test3.qvs',[tablename])


# print(myblocks.blocks.keys())
# myscript = 'ScriptOutput/output.qvs'
# myblocks.writeblock(myscript,'Main')		
