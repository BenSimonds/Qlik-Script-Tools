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
- Write block method for blocklibrarty class to write block to script file, replacing neccessary @0,@1,@2 strings. -DONE
- QVD analyser class to grab info from qvd xml header. -DONE
- QVD script writer class to generate load script block for a given qvd. -DONE (use add_qvd_block in qvstools.blocks)
- QVD directory tool to write a full load script for a directory of qvds. -DONE (use add_directory_QVD in qvstools.blocks)
- Example script to generate full load script from a directory along with an example qvw file that runs the script.

##Ideas for further tools:
- XPath based find and replace for -prj folder xml files (useful for batch editing objects).
- SQL discovery of tables and writing of standard load script.


