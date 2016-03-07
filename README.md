# Qlik-Script-Tools
Tools for quickly developing flexible Qlikview load scripts.

##Usage:
- Download library.
- Main modules are in qvstools.
- Create a block library to hold the different parts of your script.
- Add blocks to the library with blocklibrary add methods (depending on type).
- Write your load script with the block.write method.

##To do list:

- Block class as a basic container for a chunk of qlik script. -DONE
- Blocklibrary class as a container for a dict of blocks. - DONE
- Add block methods for blocklibrary class. -DONE
- Method for pickling blocks. -DONE
- Method for writing blocks as xml would be better given that a) they're only small text files, b) xml is human readable and c) the heavy use of xml elswhere in qlik/these tools.
- Write block method for blocklibrarty class to write block to script file, replacing neccessary @0,@1,@2 strings. -DONE
- QVD analyser class to grab info from qvd xml header. -DONE
- QVD script writer class to generate load script block for a given qvd. -DONE (use add_qvd_block in qvstools.blocks)
- QVD directory tool to write a full load script for a directory of qvds. -DONE (use add_directory_QVD in qvstools.blocks)
- Example script to generate full load script from a directory along with an example qvw file that runs the script.
- XPath based find and replace for -prj folder xml files (useful for batch editing objects). -IN PROGRESS

##Ideas for further tools:

- SQL discovery of tables and writing of standard load script.
- Automatic SUB-ifying of existing scripts, adding metadata stuff.
- Split tabs method for blocklibrary. Splits block at each //$tab, returns a list of blocks.


