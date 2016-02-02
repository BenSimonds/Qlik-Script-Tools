#Module for storing blocks.

from os import listdir
import sys, os, pickle
sys.path.append(os.path.realpath('Classes'))
from block import Block

class Blocks:
	"""This adds an easy way to bundle together the qvblocks scripts in a single file."""

	def __init__(self,name):
		self.name = name
		self.blocks = {}
		
		for bf in [f for f in os.listdir('Blocks')]:
			block = pickle.load(open('Blocks/'+bf,'rb'))
			self.blocks[block.name] = block
		###

	def writeblock(self,intofile,block,replacelist):
		"""Appends a block to a file."""
		print('Writing block {0} to file.'.format(block))
		#Replace @1 notation in block with user specified text.
		blocktext = self.blocks[block].text
		for replace in replacelist
		with open(intofile,'a') as outputfile:
			outputfile.write(self.blocks[block].text)
		return


myblocks = Blocks('Test')
print(myblocks.blocks.keys())
myscript = 'ScriptOutput/output.qvs'
myblocks.writeblock(myscript,'Main')		