"""Module for dealing with prj files."""
import os, sys
import xml.etree.ElementTree as ET

class QVObject:
	"""
	Class for a qlikview object. Holds the xml tree as well as it's type, name etc.
	"""

	object_types = {
		'GraphProperties':'Chart',
		'ListBoxProperties':'List',
		'BookmarkObjectProperties':'Bookmark',
		'ButtonProperties':'Button',
		'CustomObjectProperties':'Custom',
		'CurrentSelectionProperties':'CurrentSelections',
		'ContainerProperties':'Container',
		'InputBoxProperties':'Input',
		'LineArrowProperties':'Arrow',
		'MultiBoxProperties':'Multi Box',
		'StatisticsBoxProperties':'Statistics',
		'SliderProperties':'Slider',
		'SearchObjectProperties':'Search',
		'TableBoxProperties':'Table',
		'TextObjectProperties':'Text',
		##Non Object xml files:
		'SheetProperties':'Sheet', #Holds sheet properties.
		'DocInternals':'DocInternals',
		'DocProperties':'DocProperties',
		'PrjQlikViewProject':'Project', #Holds the arrangment of sheets and their child objects.
		'TopLayout':'TopLayout',
		'AllProperties':'AllProperties'
	}

	def __init__(self,object_file):
		"""Load the xml file object_file and turn it into an object."""
		self.id = os.path.basename(object_file[0:-4])
		self.path = object_file
		self.xml = ET.parse(self.path)
		self.type = self.object_types[self.xml.find('.').tag]

	def write(self,path=False):
		"""Write the object back to an xml file."""
		root = self.xml.find('.') #Root of element tree as eleent.
		ouptut_string = ET.tostring(root,encoding='UTF-8',short_empty_elements=False)
		if path: #Overwrite original file.
			output_path = path
		else:
			output_path = self.path	
		with open(output_path,'wb') as file:
			# A few start bytes (qlik expects these).
			file.write(b'\xef')
			file.write(b'\xbb')
			file.write(b'\xbf')
			# The xml part.
			file.write(ouptut_string)
			# End with whitespace (again matching native qlik output).
			file.write(b'\r\n')
			

class PRJ:
	"""
	Class for holding the component parts of a prj folder, and methods for doing useful stuff with them.
	"""
	def __init__(self,directory):
		"""Takes the """
		self.name = os.path.basename(directory)[0:-4]
		self.path = directory
		self.all_files = os.listdir(directory)
		self.objects = {}
		for file in self.all_files:
			if file.endswith('.xml'):
				try:
					ob = QVObject(os.path.join(directory,file))
					self.objects[ob.id] = ob
				except KeyError:
					print('Object type not found for file: {0}'.format(str(file)))

	def write_xml_all(self):
		"""
		Write the content of the prj object back to their original file sources.
		"""		
		for ob in self.objects.values():
			ob.write()

	def find_replace_elements(self,search_path,replace,object_id=False,object_type=False):
		"""
		Takes an xpath query and searches through self.xmlfiles to find and replace, then writes back to the source files.

		Qlik xml files seem not to use attributes so we assume that the user always wants to replace the .text of an element.

		Arguments:
		search_path -- xpath query.
		object_id -- (optional) object id of object to limit find and replace to.
		object_type -- (optional) object type of objects to limit find and replace to.

		Examples:
		Find and replace all the fonts in a project with calibri::

			prj = PRJ('App-prj')
			prj.find_replace_elements(".//FontName",'Calibri')

		"""
		if isinstance(object_id,str):
			object_id = [object_id]
		elif isinstance (object_id,list):
			pass
		else:
			object_id = self.objects.keys()
		if isinstance(object_type,str):
			object_type = [object_type]
		elif isinstance(object_type,list):
			pass
		else:
			object_type = QVObject.object_types.values()

		objects_list = [ob for ob in self.objects.values() if ob.id in object_id and ob.type in object_type]
		for ob in objects_list:
			tree = ob.xml
			results = tree.findall(search_path)
			for x in results:
				x.text = replace
			ob.xml = tree	

		#Write back to source:
		self.write_xml_all()

def replace_fonts_commandline(directory,font):
	"""Command line tool registered by setuptools as QVReplaceFonts. Takes a directory and switches all the fonts to the one specified. 

	Usage::

		> QVReplaceFonts "PrjDirectory-prj"
	"""
	prj = PRJ(directory)

	prj.find_replace_elements(".//FontName",font)			



