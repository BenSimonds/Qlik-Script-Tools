#Module for storing blocks.
import pickle
import xml.etree.ElementTree as ET
import sys, os, unicodedata

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
		with open(b_textfile,'r') as b_text:
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

	def writeblock(self,block,intofile,replacelist=[],mode='a'):
		"""Appends a block to a file."""
		print('Writing block {0} to file.'.format(block))
		#Replace @1 notation in block with user specified text.
		blocktext = self.blocks[block].text
		for i  in range(0,len(replacelist)):
			blocktext = blocktext.replace('@' + str(i),replacelist[i]) #This doesnt seem to be working...
		#Write output to file.		
		with open(intofile,mode) as outputfile:
			outputfile.write(blocktext)
		return

	def addqvdblock(self,qvd):
		"""Takes a qvd object and writes a simple load statement for it.
		Load Statement example:

		TableName:
		Load
			ID	as _KEY_ID //(optional)
		,	A	as TA_A
		,	B	as TA_B
		,	C	as TA_C
		From [Filepath.qvd] (qvd);
		"""
		
		blocktext = '\n'
		blocktext = blocktext + qvd.table + ':\nLoad\n'
		#Optionalkeyload would go here.
		for field in qvd.fields:
			blocktext = blocktext + '\t' + field + '\tas\t' + qvd.tablePrefix + field + ',\n'
		blocktext = blocktext + 'ALL_' + qvd.table.upper() + '\tas\t' + 'ALL_' + qvd.table.upper() + '\n'
		blocktext = blocktext + 'from [' + qvd.abspath + ']\n'
		blocktext = blocktext + ';\n'
		self.blocks['QVD_' + qvd.table] = Block(
			'QVD_' + qvd.table, 
			'Generated qvd block. QVD File: ' + qvd.abspath,
			'QVD',
			blocktext
			)

class QVD:
	"""Takes a qvd file and makes a python class with its xml header info."""

	def __init__(self,qvdfile):
		self.qvdheader = self.loadqvdfile(qvdfile)

		#Turn fields and table name into some useful attributes of the class.
		self.fields = [e.text for e in self.qvdheader.findall('.//FieldName')]
		self.table 	= ''.join([c for c in self.qvdheader.find('.//TableName').text if not c.isspace()])
		self.tablePrefix = self.table[0:2].upper()
		self.filename = os.path.basename(qvdfile)
		self.abspath = os.path.abspath(qvdfile)

	def loadqvdfile(self, infile):
		with open(infile,'rb') as qvdfile:
			endphrase =  '</QvdTableHeader>'
			filedata = ''
			while filedata[-len(endphrase):] != endphrase: 
				byte = qvdfile.read(1)
				try:
					x = unicodedata.category(byte.decode("utf-8",'ignore'))
				except TypeError:
					print('Unexpected end of file...')
					break	
				else:
					filedata += byte.decode("utf-8",'ignore')		
		return ET.fromstring(filedata) 

