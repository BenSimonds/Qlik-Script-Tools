.. Qlik-Script-Tools documentation master file, created by
   sphinx-quickstart on Sat Mar 19 23:28:59 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Qlik-Script-Tools
=================

Contents:

.. toctree::
   :maxdepth: 2

   modules
   ...




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

* Behold! Automated qvw generation! See below for more about subbify.

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


