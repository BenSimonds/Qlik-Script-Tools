from nose.tools import *
from qvstools.blocks import Block, BlockLibrary

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
	myblocklib.addtextblock('Testblock','Test of Main block','BlockType','tab_Main.qvs')
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
	myblocklib.addtextblock('TestReplaceBlock','TestReplaceBlock','ReplaceType','block_CallMeta.qvs')
	myblocklib.writeblock('TestReplaceBlock','test2.qvs',['TestTableName'])



# print(myblocks.blocks.keys())
# myscript = 'ScriptOutput/output.qvs'
# myblocks.writeblock(myscript,'Main')		