#Module for storing blocks.
import pickle

class Block:
	def __init__(self,b_name,b_description,b_type,b_text):
		self.name = b_name
		self.description = b_description
		self.type = b_type
		self.text = b_text


class BlockLibrary:
	"""This adds an easy way to bundle together the qvblocks scripts in a single file."""

	def __init__(self,name):
		self.name = name
		self.blocks = {}

	def addpickledblock(self,block):
		self.blocks[block] = pickle.load(open('blocks/' + block + '.p'))

	def addtextblock(self,b_name,b_description,b_type,b_textfile):
		"""Adds a block from a text file given the rest of the inputs."""
		with open('blocks/source/'+b_textfile,'r') as b_text:
			self.blocks[b_name] = Block(b_name,b_description,b_type,b_text.read())	

		
		# for bf in [f for f in os.listdir('Blocks')]:
		# 	block = pickle.load(open('Blocks/'+bf,'rb'))
		# 	self.blocks[block.name] = block
		# ###
	
	def removeblock(self,block):
		del self.blocks[block]

	def pickleblock(self,block):
		with open('blocks/'+block+'.p','wb') as blockfile:
			pickle.dump(self.blocks[block],blockfile)	

	def writeblock(self,block,intofile,replacelist):
		"""Appends a block to a file."""
		print('Writing block {0} to file.'.format(block))
		#Replace @1 notation in block with user specified text.
		blocktext = self.blocks[block].text
		for i  in range(0,len(replacelist)):
			blocktext = blocktext.replace('@' + str(i),replacelist[i]) #This doesnt seem to be working...
		#Write output to file.		
		with open(intofile,'a') as outputfile:
			outputfile.write(blocktext)
		return
