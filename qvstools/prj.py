"""Module for dealing with prj files."""
import os, sys, subprocess
import xml.etree.ElementTree as ET
from itertools import chain

object_types = {
		#Object xml files.
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
		'TextObjectProperties':'Text'
		}

other_types = {
		##Non Object xml files:
		'SheetProperties':'sheet_properties', #Holds sheet properties.
		'DocInternals':'doc_internals',
		'DocProperties':'doc_properties',
		'PrjQlikViewProject':'project', #Holds the arrangment of sheets and their child objects.
		'TopLayout':'top_layout',
		'AllProperties':'all_properties'
		}

class QVObject:
	"""
	Class for a qlikview object. Holds the xml tree as well as it's type, name etc.
	"""
	def __init__(self,object_file):
		"""Load the xml file object_file and turn it into an object."""
		self.id = os.path.basename(object_file[0:-4])
		self.path = object_file
		self.xml = ET.parse(self.path)
		self.is_object = self.xml.find('.').tag in object_types
		if self.is_object:
			self.type = object_types[self.xml.find('.').tag]
		elif self.xml.find('.').tag in other_types:
			self.type = other_types[self.xml.find('.').tag]
		else:
			raise KeyError('Unrecognised qlikview object type: {0}'.format(self.xml.find('.').tag))

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
				ob_working = QVObject(os.path.join(directory,file))
				if ob_working.is_object:
					self.objects[ob_working.id] = ob_working
				else:
					setattr(self,ob_working.type,ob_working) ###WIP...

	def write_xml_all(self):
		"""
		Write the content of the prj object back to their original file sources.
		"""		
		for ob in self.objects.values():
			ob.write()
		self.sheet_properties.write()
		self.doc_internals.write()
		self.doc_properties.write()
		self.project.write()
		self.top_layout.write()
		self.all_properties.write()


	def find_replace_elements(self,search_path,replace,object_id=False,object_type=False):
		"""
		Takes an xpath query and searches through self.xmlfiles to find and replace, then writes back to the source files.

		Qlik xml files seem not to use attributes so we assume that the user always wants to replace the .text of an element.

		:param search_path: xpath query.
		:param object_id: object id of object to limit find and replace to. Leave as default to search all objects.
		:param object_type: object type of objects to limit find and replace to. Leave as default to search all object types.

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
			object_type = object_types.values()

		objects_list = [ob for ob in self.objects.values() if ob.id in object_id and ob.type in object_type]
		print('Found {0} Elements.'.format(len(objects_list)))
		for ob in objects_list:
			tree = ob.xml
			results = tree.findall(search_path)
			for x in results:
				x.text = replace
			ob.xml = tree	

		#Write back to source:
		self.write_xml_all()

	def rescale_layout(self,new_x,new_y,sheets='all',global_rescale=False):
		"""
		Takes the layout and scales it to a new resolution.

		Uses the maximum x and y coordinates of objects in the sheet and rescales all of the layout coordinates to match the resoltion given.
		For best results add a text box in the lower rightmost corner of your sheet to mark the current bounds of the sheet.
		:param new_x: New x resolution to scale to in pixels.
		:param new_y: New y resolution to scale to in pixels.
		:param sheets: List of sheet IDs e.g. ['SH01','SH02'] to rescale. If left as the default, all sheets will be rescaled.
		:param global_rescale: Set this to True to use the max x and y coords of *any* sheet to generate the scaling factors for all sheets.
		The default behaviour is to rescale each sheet based on it's own max x and y coordinates.
		"""
		new_x,new_y = (new_x*3.125,new_y*3.125) #Not sure why qlik scales up pixels by this factor but it does...

		sheet_elements = [s for s in self.project.xml.findall('.//SHEETS/PrjSheetProperties') if s.find('./SheetId').text.split('\\')[1] in sheets or sheets == 'all'] 
		if global_rescale:
			coords = list(chain.from_iterable([sh.findall('.//Rect') for sh in sheet_elements]))
			max_x = max([float(x.find('./Left').text) + float(x.find('./Width').text) for x in coords])
			max_y = max([float(y.find('./Top').text) + float(y.find('./Height').text) for y in coords])
			scale_x,scale_y = (new_x/max_x,new_y/max_y)

			for c in coords:
				c.find('./Left').text 	= str(int(float(c.find('./Left').text)	* scale_x))
				c.find('./Top').text 	= str(int(float(c.find('./Top').text)		* scale_y))
				c.find('./Width').text 	= str(int(float(c.find('./Width').text)	* scale_x))
				c.find('./Height').text = str(int(float(c.find('./Height').text)	* scale_y))
		else:		
			for ele in sheet_elements:
				coords = ele.findall('.//Rect')
				max_x = max([float(x.find('./Left').text) + float(x.find('./Width').text) for x in coords])
				max_y = max([float(y.find('./Top').text) + float(y.find('./Height').text) for y in coords])
				scale_x,scale_y = (new_x/max_x,new_y/max_y)

				for c in coords:
					c.find('./Left').text 	= str(int(float(c.find('./Left').text)	* scale_x))
					c.find('./Top').text 	= str(int(float(c.find('./Top').text)		* scale_y))
					c.find('./Width').text 	= str(int(float(c.find('./Width').text)	* scale_x))
					c.find('./Height').text = str(int(float(c.find('./Height').text)	* scale_y))

		self.project.write()


def replace_fonts_commandline():
	"""Command line tool registered by setuptools as QVReplaceFonts. Takes a qvw file and switches all the fonts to the one specified. 

	Usage::

		> QVReplaceFonts "PrjDirectory-prj" "Comic Sans"
	"""
	error_message = 'Please supply a prj folder or qvw file to replace fonts in, and the font you want to use. ie. QVReplaceFonts "PrjDirectory-prj" "Comic Sans" '

	args = sys.argv
	try:
		if args[1].endswith('-prj'):
			prjdir = args[1]
			qvw = prjdir[0:-4] + '.qvw'
			print(qvw)
		elif args[1].endswith('.qvw'):
			qvw = args[1]
			prjdir = qvw[0:-4] + '-prj'
		else:
			print(error_message)
			return
		font = args[2]
	except IndexError:
		print(error_message)
		return
	try:
		flags = args[3:]
	except IndexError:
		pass

	#We can use flags to add some extra functionality
	open_after = '-o' in flags

	#Sense check input:
	if not os.path.isfile(qvw) and qvw.endswith('.qvw'):
		print('Cannot find file: {0}'.format(qvw))
		return None
	elif not (os.path.isdir(prjdir)):
		print('Cannot find a prj directory, have you generated one?')
		return None
	else:
		prj = PRJ(prjdir)
		prj.find_replace_elements(".//FontName",font)		

	if open_after:
		subprocess.Popen(["C:\Program Files\QlikView\qv.exe",qvw])	



