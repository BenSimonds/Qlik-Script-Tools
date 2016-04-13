"""Module for creating and combining blocks."""
try:
	import lxml.etree as ET
	print("running with lxml.etree")
except ImportError:
	import xml.etree.ElementTree as ET
	print("running with xml.etree")
import sys, os, unicodedata, re
from qvstools.text import known_encodings
from qvstools.qvd import QVD
from qvstools.regex_store import searches


class Block:
	"""Container for a block of qlik script.

	:param name: the name for your block.
	:param description: longer description of your block
	:param blocktype: currently not much used, but useful for grouping blocks within a library.
	:param blocktext: string containing the actual text of your block.
	:param replacelist: list of strings to use as replacements for @0,@1...
	"""
	def __init__(self,name,description,blocktype,blocktext,replacelist=[]):
		self.name = name
		self.description = description
		self.type = blocktype
		self.text = self.strip_non_unicode(blocktext)
		self.replacelist = replacelist

	def write(self,pathname,replacelist=[],mode='a'):
		"""Write block to pathname.

		:param replacelist: list of strings to use as replacements for @0,@1...
		:param mode: same as for normal write() method. 'w' for write, 'a' for append.
		"""
		#Check that replacelist length is correct for block.
		if len(replacelist) != len(self.replacelist):
			raise NameError('Replacelist requires {0} items but supplied {1}.'.format(len(self.replacelist),len(replacelist)))
			return
		#Replace @1 notation in block with user specified text.
		blocktext = self.text
		for i  in range(0,len(replacelist)):
			blocktext = blocktext.replace('@' + str(i),replacelist[i]) #This doesnt seem to be working...
		#Write output to file.		
		with open(pathname,mode,encoding=known_encodings['block_qvs']) as outputfile:
			outputfile.write(blocktext)
		return

	def strip_non_unicode(self,input_data):
		#Strip non unicode characters out of weird qlik export text...
		if isinstance(input_data,str):
			return input_data
		else:
			assert isinstance(input_data,bytes), 'Input not byte or string...'
			print('Converting input text to unicode assuming utf-8. May result in missing characters....')
			return inputt_data.decode('utf-8',errors='ignore')
		
class BlockLibrary:
	"""Bundles together several blocks and provide methods for working with them.

	A blocklibrary brings together several blocks as a dict within self.blocks. 
	This makes it easy to combine several blocks to write more complex scripts.
	:param load_defaults: if True will load a default set of blocks.
	"""

	def __init__(self,name,load_defaults=False):
		self.name = name
		self.blocks = {}
		if load_defaults:
			dir_defaults = os.path.join(os.path.dirname(__file__),'../blocks')
			for xmlfile in [f for f in os.listdir(dir_defaults) if f.startswith('Default_') and f.endswith('.p')]:
				self.add_xml_block(os.path.join(dir_defaults,xmlfile))
		else:
			pass

	def add_text_block(self,name,description,blocktype,pathname):
		"""Create a Block and adds it to the library.

		:param name: name of the block. Needn't be the same as pathname.
		:param description: description of the block.
		:param blocktype: currently not much used, but useful for grouping blocks within a library.
		:param pathname: filepath of text file (qvs/txt) to turn into a block.
		"""
		with open(pathname,'r') as textfile:
			blocktext = textfile.read()
			replacelist = re.findall(r"//\((@[\d]),\s?\'([\w\s,.?!()$]*)\'\)",blocktext) #Returns a list of tuples. 
			#Scrub replacelist lines from text file.
			blocktext = '\n'.join([line for line in blocktext.split('\n') if not re.search(r"//\(@[\d]",line) ])
			
			self.blocks[name] = Block(name,description,blocktype,blocktext,replacelist)	

	def write_block(self,blockname,outputfile,replacelist=[],mode='a'):
		"""Call write() method of block.

		:param blockname: name of block to write."""
		self.blocks[blockname].write(outputfile,replacelist,mode)

	def remove_block(self,blockname):
		"""Remove block from library."""
		del self.blocks[blockname]
			
	def block_to_xml(self,blockname,directory='.'):
		"""Takes the name of a block as a string and writes an xml file containing both 
		the block text and its metadata (name, description, type, replacelist).

		:param blockname: name of block to write to xml.
		:param directory: by default this method writes to the current directory, but you can specify on here.
		"""
		block = self.blocks[blockname]	# Get block by name.
		block_xml = ET.Element('block')
		ET.SubElement(block_xml,'name')
		block_xml.find('name').text = block.name
		ET.SubElement(block_xml,'description')
		block_xml.find('description').text = block.description
		ET.SubElement(block_xml,'type')
		block_xml.find('type').text = block.type
		ET.SubElement(block_xml,'text')
		block_xml.find('text').text = block.text
		ET.SubElement(block_xml,'replacelist')
		for item in block.replacelist:
			item_el = ET.Element('replacelistitem',id=item[0])
			item_el.text = item[1]
			block_xml.find('replacelist').append(item_el)
		tree = ET.ElementTree(element = block_xml)
		filepath = os.path.join(directory,block.name+'.xml')
		tree.write(filepath,encoding=known_encodings['block_xml'],short_empty_elements=False)

	def add_xml_block(self,filepath):
		"""Create a block from an xml file and add it to the library."""
		xmlfile = ET.parse(filepath)
		b_name = xmlfile.find('./name').text
		b_description = xmlfile.find('./description').text
		b_type = xmlfile.find('./type').text
		b_text = xmlfile.find('./text').text
		b_replacelist = []
		for x in xmlfile.findall('.//replacelistitem'):
			b_replacelist.append((x.get('id'),x.text))
		self.blocks[b_name] = Block(
			b_name,
			b_description,
			b_type,
			b_text,
			b_replacelist)
		
	def add_qvd_block(self,qvd,blockname='',tablename=False,prefix=False):
		"""Read in a qvd file using QVD() and create a block containing a simple load statement for it.

		Example Output::

			TableName:
			Load
				ID	as _KEY_ID //(optional)
			,	A	as TA_A
			,	B	as TA_B
			,	C	as TA_C
			From [Filepath.qvd] (qvd);

		"""
		qvd = QVD(qvd,tablename,prefix)
		if blockname:
			qvdname = blockname
		else:
			qvdname = 'QVD_' + os.path.basename(qvd.filename)[0:-4]	
		blocktext = '\n'
		blocktext = blocktext + qvd.table + ':\nLoad\n'
		for field in qvd.fields:
			blocktext = blocktext + '\t[' + field + ']\tas\t[' + qvd.tablePrefix + field + '],\n'
		blocktext = blocktext + '\t' + "'ALL_" + qvd.table.upper() + "'\tas\t" + 'ALL_' + qvd.table.upper() + '\n'
		blocktext = blocktext + 'from [' + qvd.abspath + '] (qvd)\n'
		blocktext = blocktext + ';\n'
		self.blocks[qvdname] = Block(
			'QVD_' + qvd.table, 
			'Generated qvd block. QVD File: ' + qvd.abspath,
			'QVD',
			blocktext
			)

	def add_directory_qvd(self,directory):
		"""Create blocks for all .qvd files in directory."""
		files = [f for f in os.listdir(directory) if os.path.basename(f).endswith('.qvd')]
		for f in files:
			self.add_qvd_block(os.path.join(directory,f))

	def add_directory_block(self,directory):
		"""Create blocks for all .xml files in directory."""		
		files = [f for f in os.listdir(directory) if os.path.basename(f).endswith('.xml')]
		for f in files:
			self.add_xml_block(f)
	

	@staticmethod
	def write_tab(tabname,pathname,mode='a'):
		"""Write a single ///$tab to the file specified by pathname."""
		with open(pathname,mode) as outputfile:
			outputfile.write('\n///$tab ' + tabname + '\n')
		return

	@staticmethod
	def split_block_tabs(block):
		"""Split the input block at each ///$tab line and return a list of blocks.

		The returned list will *not* be added to the blocklibray. To add it just to a simple for loop::

			for sub_block in myblocklibrary.split_block_tabs(block):
				myblocklibrary[sub_block.name] = sub_block

		The reason for this behavior is that the block libray dict is unordered, but it is useful to preserve the order the blocks were split into.
		Note that this method takes a block, not the name of a block in the library. This is so that the method can be called as a staticmethod independently of a blocklibray object.
		Used for example by :func:`subbify <qvstools.subbify.subbify>`. 
		"""
		blocktext = block.text
		#Tab looks like //$tab something.
		tabs = [] #will be a list of blocks.
		blocklines = blocktext.split('\n')
		#Find intervals between tabs.
		counter = 0
		tablines = []
		for i in range(0,len(blocklines)):
			if blocklines[i].startswith('///$tab'):
				tablines.append((i,blocklines[i][7:].strip())) #Tuple: (line of blocklines that tab starts, name of tab)
		for i in range(0,len(tablines)):
			if i == len(tablines)-1: #If on last tab, take all the way to the end.
				tab_text = '\n'+'\n'.join(blocklines[tablines[i][0]+1:])+'\n'
			else: #Else take from start +1 (to avoid tab line) up to next tab start.
				tab_text = '\n'+'\n'.join(blocklines[tablines[i][0]+1:tablines[i+1][0]])+'\n'
			tab_name = tablines[i][1].strip()
			tab_block = Block(
				tab_name,
				'tab belonging to block: {0}'.format(block.name),
				'TAB',
				tab_text
				)
			tabs.append(tab_block)
			
		return tabs #Return a list that can be iterated over in the correct order.
	
	@staticmethod
	def find_referenced_files(block):
		"""
		Scan the block with a regular expression that matches qvds, return a list of the qvds it references.
		"""

		blocktext = block.text
		
		print(filesearchstring)
		filesearch = searches['filesearchstring2']
		storesearch = searches['store_statement']
		commentsearch = re.compile(r"\\\\")

		matchlines = []
		blocklines =  blocktext.split('\n')
		optype = 'LOAD'	#By default expect matches to be load statements.
		for i in range(0,len(blocklines)):
			line = blocklines[i].lower()#Covert to lowercase for case insensitive search.
			if re.match(commentsearch,line): ##Line is commented.
				pass
			else:
				if re.search(storesearch,line):
					optype = 'STORE'
				s = re.search(filesearch,line)
				if s:
					for g in s.groups():
						matchlines.append({
							'line':i+1,
							'text':line,
							'file':g,
							'type':optype})
					#reset optype
					optype = 'LOAD'
		return matchlines

