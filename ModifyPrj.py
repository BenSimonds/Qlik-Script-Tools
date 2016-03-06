#First stab at editing the contents of a prj folder with python and xpath.


import sys, os
import xml.etree.ElementTree as ET


prjfolder = 'QVW/TestPRJ-prj'
prjfiles = os.listdir(prjfolder)
#Create an element tree instance per xml file.
xmlfiles = [(os.path.join(prjfolder,file),ET.parse(os.path.join(prjfolder,file))) for file in prjfiles if file.endswith('.xml')]


diff = ''

#Find all font based elements inside objects.
#These have different names but all have a FontName child element.
# for x in xmlfiles:
# 	for result in x.findall('.//FontName/..'):
# 		print(result.tag)

#Set fonts for all text objects:
text_objects = [x for x in xmlfiles if x[1].find('.').tag == 'TextObjectProperties']
for x in text_objects:
	search = x[1].findall('.//FontName/..') #All elements with a child element called FontName
	for el in search:
		el.find('FontName').text = 'Calibri'
		pass
	output = ET.tostring(x[1].find('.'),encoding='UTF-8',short_empty_elements=False)
	#print(output)
	with open(x[0]+diff,'wb') as file:
		file.write(b'\xef')
		file.write(b'\xbb')
		file.write(b'\xbf')
		file.write(output)
		file.write(b'\r\n')




# for x in text_objects:
# 	print(x[0])
# 	with open(x[0],'r') as a:
# 		with open(x[0]+'test','r') as b:
# 			a_lines = a.readlines()
# 			b_lines = b.readlines()
# 			for i in range(0,len(a_lines)):
# 				if a_lines[i] == b_lines[i]:
# 					pass
# 				else:
# 					print('Line {0} differs:'.format(i+1))
# 					print(a_lines[i])
# 					print('!=')
# 					print(b_lines[i])
# 			print(a.read() == b.read())