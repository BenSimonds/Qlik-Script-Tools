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
from qvstools.blocks import *

inputfile = 'qvexports/Subbify_TestInput.qvs'
qvwsource = 'QVW/Subbify_Source'
outputfolder = 'subbify_build'
if os.path.isdir(outputfolder):
	shutil.rmtree(outputfolder)
shutil.copytree(qvwsource,outputfolder)
#Copy empty qvw to foler and make 
outputfile = os.path.join(outputfolder,'Subbified-prj\LoadScript.txt')

print('###	BUILDING BLOCK LIBRARY	###')
#Init library
bl = BlockLibrary('Main')

#Add subbify blocks:
for f in [f for f in os.listdir('blocks') if f.startswith('Subbify') and f.endswith('.xml')]:
	bl.add_xml_block(os.path.join('blocks',f))

print(bl.blocks.keys())

#Add block for input script:
bl.add_text_block(
	'INPUT',
	'Input to be subbified',
	'INPUT',
	inputfile)
tabs = bl.split_block_tabs(bl.blocks['INPUT']) 

print('###	TABS FOUND	###')
print([tab.name for tab in tabs])

#Now subbify it!
#Start writing our qvs script:
print('###	WRITING TABS	###')
bl.blocks['Subbify_Main'].write(outputfile,mode='w')
bl.blocks['Subbify_SmartCall_Init'].write(outputfile)
bl.blocks['Subbify_Sub_Metadata'].write(outputfile)
write_tab('<',outputfile)
sublines = ''
for tab in bl.split_block_tabs(bl.blocks['INPUT']): ##Each one is a block remember.
	sublines = sublines + tab.name + '\n'
	bl.blocks['Subbify_Template_Start'].write(outputfile,[tab.name,'NONE']) ##No tables in our example for now... but need a replacelist for this block.
	tab.write(outputfile)
	bl.blocks['Subbify_Template_End'].write(outputfile)
write_tab('>',outputfile)	
bl.blocks['Subbify_SmartCall_Run'].write(outputfile,[sublines])


