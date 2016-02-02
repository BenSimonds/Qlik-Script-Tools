"""
Script for generating block files from source qvs files and pickling them.
"""

from os import listdir
import sys, os, pickle
sys.path.append(os.path.realpath('Classes'))
from block import Block

# b_file = input('Enter the filename of a block file in QVBlocks to pickle:')
# b_name = input('Enter a name for this block.')
# b_description = input('Enter A description for this block')
# b_type = input('Select a type for this block. \n 1. Plain text \n 2.Text with repacement string (e.g. vars, names)')

b_file = 'tab_Main.qvs'
b_name = 'Main'
b_type = 1
b_description = 'Standard QV start block.'


with open('QVBlocks/' + b_file,'r') as inputfile:
	b_text = inputfile.read()

#Build block file (picked version) as a class

newBlock = Block(b_name,b_description,b_type,b_text)
print(newBlock.text)

with open('Blocks/'+b_name+'.p','wb')	as f:
	pickle.dump(newBlock,f)
