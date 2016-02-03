#A basic script to get to grips with chaining together blocks of text.

import sys, os
sys.path.append(os.path.realpath('..'))


#Load some blocks

block1 = open('QVBlocks/tab_Main.qvs','r').read()


#Generate a new file from those blocks:

myscript = open('ScriptOutput/output.qvs', 'w')

myscript.write(block1)

myscript.close()
