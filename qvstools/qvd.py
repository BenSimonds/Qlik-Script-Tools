"""Tools for manipulating qvd files."""
import sys,os
from qvstools.text import known_encodings
try:
	import lxml.etree as ET
	print("running with lxml.etree")
except ImportError:
	import xml.etree.ElementTree as ET
	print("running with xml.etree")

class QVD:
	"""Take a qvd file and make a python class with its xml header info.

	:param qvdfile: filepath of qvdfile to create block for. 
	:param tablename: replaces the name of the table in the qvd with the string given.	
	:param prefix: specifies a prefix to be used when aliasing fieldnames in table, i.e. if prefix = 'XX', FieldName will be aliased as XX_FieldName in the load statement.
	"""

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
		# Read the xml header of a qvd file and parse it as xml.
		encoding = known_encodings['qvd']
		with open(infile,'rb') as qvdfile:
			startphrase = '<QvdTableHeader>'
			endphrase =  '</QvdTableHeader>'
			#Read data until endphrase is found or we hit garbage...
			start  = 0
			span = qvdfile.read(len(endphrase)).decode(encoding)
			filedata = span
			while span != endphrase:
				start += 1				#increment start by 1
				qvdfile.seek(start)		#read the new span.
				span = qvdfile.read(len(endphrase)).decode(encoding) #get new span
				filedata += span[-1]	#Add last char of span
			assert isinstance(filedata,str) , "QVD header hasn't been decoded to unicode. oops!" #Unicode dammit!
		return ET.fromstring(filedata)
