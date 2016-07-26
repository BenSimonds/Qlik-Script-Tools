from qvstools.prj import *
import subprocess

prjfolder = r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\qvstools\tests\testdata\TestPRJ-prj"
qvwfile = r"C:\Users\ben.simonds\Documents\QVPythonTools\Qlik-Script-Tools-Minimal\qvstools\tests\testdata\TestPRJ.qvw"

prj = PRJ(prjfolder)
new_x,new_y = (1920*3.125,1080*3.125) #Not sure why qlik scales up pixels by this factor but it does...
print(new_x,new_y)

coords = prj.project.xml.findall('.//SHEETS/PrjSheetProperties[SheetId="Document\\SH04"]//Rect')
max_x = max([float(x.find('./Left').text) + float(x.find('./Width').text) for x in coords])
max_y = max([float(y.find('./Top').text) + float(y.find('./Height').text) for y in coords])
print(max_x,max_y)

scale_x,scale_y = (new_x/max_x,new_y/max_y)
print(scale_x,scale_y)

#Get a list of rectangles:
#mysheet = [x for x in prj.project.xml.findall('.//SHEETS/PrjSheetProperties[SheetId="Document\\SH04"]//Rect')]
#print(len(mysheet))
#ET.dump(mysheet[0])

for c in coords:
	c.find('./Left').text 	= str(int(float(c.find('./Left').text)	* scale_x))
	c.find('./Top').text 	= str(int(float(c.find('./Top').text)		* scale_y))
	c.find('./Width').text 	= str(int(float(c.find('./Width').text)	* scale_x))
	c.find('./Height').text = str(int(float(c.find('./Height').text)	* scale_y))
	#ET.dump(c)

prj.project.write()
subprocess.Popen(["C:\Program Files\QlikView\qv.exe",qvwfile])