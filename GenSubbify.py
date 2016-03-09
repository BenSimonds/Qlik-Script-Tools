"""
GEN SUBBIFY:
Aim: to aut-generate a subbiified qvd loader / extractor based on a script input.
Steps:
1. Take input script:
2. Split into tabs.
3. Wrap each tab in subbify blocks.
4. Save out resulting script into cloned prj directory for cloned empty/template file.
"""
import os, sys, shutil
import subprocess
from qvstools.blocks import *

print('Setting Up.')

inputfile = 'qvexports/Subbify_TestInput.qvs'
qvwsource = 'QVW/Subbify_Source'
outputfolder = 'subbify_build'
if os.path.isdir(outputfolder):
	shutil.rmtree(outputfolder)
shutil.copytree(qvwsource,outputfolder)
#Copy empty qvw to foler and make 
outputfile = os.path.join(outputfolder,'Subbified-prj\LoadScript.txt')

print('Building Block Library')

#Init library
bl = BlockLibrary('Main')

#Add subbify blocks:
for f in [f for f in os.listdir('blocks') if f.startswith('Subbify') and f.endswith('.xml')]:
	bl.add_xml_block(os.path.join('blocks',f))

#Add block for input script:
bl.add_text_block(
	'INPUT',
	'Input to be subbified',
	'INPUT',
	inputfile)
tabs = bl.split_block_tabs(bl.blocks['INPUT']) 

print('{0} Tabs Found'.format(len(tabs)))
for tab in tabs:
	print('\t' + tab.name)


print('Writing Tabs')

bl.blocks['Subbify_Main'].write(outputfile,mode='w')
bl.blocks['Subbify_SmartCall_Init'].write(outputfile)
bl.blocks['Subbify_Sub_Metadata'].write(outputfile)
write_tab('<',outputfile)
sublines = ''
smartvar = '_'
for tab in tabs: ##Each one is a block remember.
	sublines = sublines + tab.name + '\n'
	smartvar = smartvar + tab.name + '_'
	bl.blocks['Subbify_Template_Start'].write(outputfile,[tab.name,tab.name]) ##No tables in our example for now... but need a replacelist for this block.
	tab.write(outputfile)
	bl.blocks['Subbify_Template_End'].write(outputfile)
write_tab('>',outputfile)	
bl.blocks['Subbify_SmartCall_Run'].write(outputfile,[sublines,smartvar])


print('Launch Qlikview, Open And Reload')

qvw_abspath = os.path.join(os.path.abspath(outputfolder),'Subbified.qvw')
varstring = '/vvSmartVarPassedFromExternalCall='+smartvar
subprocess.Popen(["C:\Program Files\QlikView\qv.exe",qvw_abspath,varstring,'/l'])

print('Finished!')
