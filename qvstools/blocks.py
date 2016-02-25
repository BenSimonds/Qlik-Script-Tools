#Module for storing blocks.
import pickle
import xml.etree.ElementTree as ET
import sys, os, unicodedata, re

class Block:
	def __init__(self,b_name,b_description,b_type,b_text,b_replacelist=[]):
		self.name = b_name
		self.description = b_description
		self.type = b_type
		self.text = b_text
		self.replacelist = b_replacelist

		
class BlockLibrary:
	"""This adds an easy way to bundle together the qvblocks scripts in a single file."""

	def __init__(self,name,load_defaults=False):
		self.name = name
		if load_defaults:
			for pfile in ['Blocks' + f for f in os.listdir('Blocks') if f.startswith(Default_)]:
				addpickledblock(pfile)
		else:
			self.blocks = {}

	def addpickledblock(self,blockfile):
		self.blocks[block] = pickle.load(open(blockfile,'rb'))

	def addtextblock(self,b_name,b_description,b_type,b_textfile):
		"""Adds a block from a text file given the rest of the inputs."""
		with open(b_textfile,'r') as textfile:
			b_text = textfile.read()
			b_replacelist = re.findall(r"//\((@[\d]),\s?\'([\w\s,.?!()$]*)\'\)",b_text) #Returns a list of tuples. 
			#self.replacelist = list(set(re.findall(r'@[\d]',self.text))) #List of items to be replaced. 
			
			self.blocks[b_name] = Block(b_name,b_description,b_type,b_text,b_replacelist)	

		
		# for bf in [f for f in os.listdir('Blocks')]:
		# 	block = pickle.load(open('Blocks/'+bf,'rb'))
		# 	self.blocks[block.name] = block
		# ###
	
	def removeblock(self,block):
		del self.blocks[block]

	def pickleblock(self,block):
		with open('Blocks/'+block+'.p','wb') as blockfile:
			pickle.dump(self.blocks[block],blockfile)

	def writeblock(self,blockname,intofile,replacelist=[],mode='a'):
		"""Appends a block to a file."""
		block = self.blocks[blockname]
		#Check that replacelist length is correct for block.
		if len(replacelist) != len(block.replacelist):
			raise NameError('Replacelist requires {0} items but supplied {1}.'.format(len(block.replacelist),len(replacelist)))
			return
		print('Writing block {0} to file.'.format(blockname))
		#Replace @1 notation in block with user specified text.
		blocktext = block.text
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
			blocktext = blocktext + '\t[' + field + ']\tas\t[' + qvd.tablePrefix + field + '],\n'
		blocktext = blocktext + '\t' + "'ALL_" + qvd.table.upper() + "'\tas\t" + 'ALL_' + qvd.table.upper() + '\n'
		blocktext = blocktext + 'from [' + qvd.abspath + '] (qvd)\n'
		blocktext = blocktext + ';\n'
		self.blocks['QVD_' + qvd.table] = Block(
			'QVD_' + qvd.table, 
			'Generated qvd block. QVD File: ' + qvd.abspath,
			'QVD',
			blocktext
			)

class QVD:
	"""Takes a qvd file and makes a python class with its xml header info."""

	def __init__(self,qvdfile,tablename=False,prefix=False):
		self.qvdheader = self.loadqvdfile(qvdfile)
		
		def setprops(qvdfile,tablename,prefix):
			#Turn fields and table name into some useful attributes of the class.
			##First do attributes that will be used in the script, here we can transform them to be more useful.
			self.fields = [e.text for e in self.qvdheader.findall('.//FieldName')]
			if tablename:
				self.table = tablename
			else:
				self.table 	= ''.join([c for c in self.qvdheader.find('.//TableName').text if not c.isspace()])
			if prefix:
				self.tablePrefix = prefix + '_'
			else:
				self.tablePrefix = self.table[0:2].upper() + '_'
			self.filename = os.path.basename(qvdfile)
			self.abspath = os.path.abspath(qvdfile)
			##Second covert some of the xml items into attributes directly. These are more for information purposes. Here we preserve Names from the
			self.CreatorDoc = self.qvdheader.find('.//CreatorDoc').text
			self.CreateUtcTime = self.qvdheader.find('.//CreateUtcTime').text

		setprops(qvdfile,tablename,prefix)

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


