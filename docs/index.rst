.. Qlik-Script-Tools documentation master file, created by
   sphinx-quickstart on Sat Mar 19 17:19:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Qlik-Script-Tools
=================

Qlik-Script-Tools is a set of tools for speeding up tedious tasks in Qlikview. So far it contains some useful tools for buidling load scripts from modular elements as well as a couple of tools for making changes to prj files procedurally. As time goes on I'll expand and improve these tools. See the todo list below for my current list of ideas.

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Installation
------------

* Checkout Qlik-Script-Tools from github:: 

	git checkout https://github.com/BenSimonds/Qlik-Script-Tools

* Start using! You can start by trying subbify on a qvs script::

	subbify "MyScript.qvs"

* Behold! Automeated qvw generation! See below for more about subbify.

Current Features
----------------

* Block class acts as a container for a chunk of Qlik script. Blocks can be imported from plain text, or from structured xml files.
* BlockLibrary class combines a container for a bunch of blocks as well as methods for creating, storing and manipulting blocks, as well as writing their content to qvs files.
* QVD class allows you to read in the xml header of a qvd file, providing access to it's metadata such as creator doc, reload date, fields, etc.
* BlockLibary can also create blocks from QVD classes. This allows for reading in a qvd, and then writing the load script to load it into a file.
* Batch loading of qvds from a directory can also be done.
* Some blocks have replace lists. This allows for string replacement within a block, for example to pass variables or rename tables.
* PRJ class has tools for reading in a prj folder, with XPath based find and replace for xml files (useful for batch editing objects).
* Subbify tool - load in an existing qvs script, and subbify will generate a qvw file with each tab made into a separate subroutine, useful for making ETL scripts modular.


Examples
--------

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
