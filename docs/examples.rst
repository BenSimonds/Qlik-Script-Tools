.. _examples:
Examples
========

Creating a new block library and adding a block::
	
	from qvstools.blocks import *

	bl = BlockLibrary('MyBlockLibrary') #Create a block library.
	bl.add_text_block(
		'MyBlock',							#Name
		'A small block of qlikview script', #Description
		'Block',							#Type
		'Script.qvs'						#Block to be added.
		)

Blocks are just normal qvs script, but you can specify strings to be replaced with the syntax below::

	//(@0,'First Replace String')
	
	//Normal qlik script from here on.
	
	@0:
	Load
		1		as ID
		'Text'	as Text
		10		as Value
	AutoGenerate 1;

You can then write the block to a file with the block.write() method, the replacelist argument accepts a list of items to replace::

	bl.write_block('MyBlock',['MyTable'])

write_block supports the usual python write modes (w or a), but defaults to a to allow you to chain blocks together easily.

The resulting output file::
	
	//Normal qlik script from here on.
	
	MyTable:
	Load
		1		as ID
		'Text'	as Text
		10		as Value
	AutoGenerate 1;

You can save useful blocks into xml files for reapeated use without entering descriptions and names every time::

	bl.block_to_xml('MyBlock')

Blocks can also be created from QVD's::
	
	bl.add_qvd_block('Data.qvd')

Directories can also be batch loaded::
	
	#Load a directory of block xml files
	bl.add_directory_blocks('Directory_Blocks')
	#or QVDs:
	bl.add_directory_QVDs('Directory_QVDs')
