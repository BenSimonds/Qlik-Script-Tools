"""
Auto-generates a subbified qvd loader / extractor based on a script input.

Steps
-----
1. Take input script:
2. Split into tabs.
3. Wrap each tab in subbify blocks.
4. Save out resulting script into cloned prj directory for cloned empty/template file.
"""
import os, sys, shutil
import subprocess
from qvstools.blocks import *

def subbify(filepath, open_after = True, reload_after = 's'):
	"""
	Base method for subbify. Takes a filepath and generates a subbified qvw file.

	Arguments:
	filepath -- should point to a qvs file. possibly in future a qvw file if I can figure out how to generate the prj files for it.
	open_after -- opens the generated file in qlikview.
	reload_after:
		s: loads sub table only. (default)
		f: loads sub table and runs all subs.
	"""

	if not filepath.endswith('.qvs'):
		print('Invalid file type, please supply the path to a qvs file.')
	else:
		print('Creating project.')
		inputfile = os.path.basename(filepath)
		inputfilename = os.path.basename(filepath)[0:-4] #filename minus the .qvs
		outputfolder = os.path.dirname(filepath)
		scriptpath = os.path.dirname(__file__)
		qvwsource = os.path.join(scriptpath,'subbify_source','Subbified.qvw')
		prjsource = os.path.join(scriptpath,'subbify_source','Subbified-prj')
		blocksource = os.path.join(scriptpath,'subbify_source')
	
		#Copy files to outputfolder.
		outputqvw = os.path.join(outputfolder,inputfilename + '_Subbified.qvw')
		outputprj = os.path.join(outputfolder,inputfilename + '_Subbified-prj')
		shutil.copy(qvwsource,outputqvw)
		if os.path.isdir(outputprj):
			print('Prj folder found, deleting.')
			shutil.rmtree(outputprj)
		shutil.copytree(prjsource,outputprj)

		#Set script file to be made:
		outputscript = os.path.join(outputfolder,inputfilename+'_Subbified-prj\LoadScript.txt')

		print('Building Block Library')

		#Init library
		bl = BlockLibrary('Main')

		#Add subbify blocks:
		for f in [f for f in os.listdir(blocksource) if f.endswith('.xml')]:
			bl.add_xml_block(os.path.join(blocksource,f))

		#Add block for input script:
		bl.add_text_block(
			'INPUT',
			'Input to be subbified',
			'INPUT',
			filepath)
		tabs = bl.split_block_tabs(bl.blocks['INPUT']) 

		print('{0} Tabs Found'.format(len(tabs)))
		for tab in tabs:
			print('\t' + tab.name)


		print('Writing Tabs')

		sublines = '\n'.join([tab.name.replace(' ','') for tab in tabs])
		smartvar = '_' + '_'.join([tab.name for tab in tabs]) + '_'

		bl.blocks['Subbify_Main'].write(outputscript,mode='w')
		bl.blocks['Subbify_SmartCall_Init'].write(outputscript,[sublines])
		bl.blocks['Subbify_Sub_Metadata'].write(outputscript)
		bl.write_tab('<',outputscript)
		for tab in tabs: ##Each one is a block remember.
			subname = tab.name.replace(' ','')
			tablename = tab.name
			bl.blocks['Subbify_Template_Start'].write(outputscript,[subname,tablename]) ##No tables in our example for now... but need a replacelist for this block.
			tab.write(outputscript)
			bl.blocks['Subbify_Template_End'].write(outputscript)
		bl.write_tab('>',outputscript)	
		bl.blocks['Subbify_SmartCall_Run'].write(outputscript)


	if open_after:
		print('Launching Qlikview')
		if reload_after == 's':
			varstring = '/vvSmartVarExternal=_'
		elif reload_after == 'f':
			varstring = '/vvSmartVarExternal='+smartvar
		if reload_after:
			subprocess.Popen(["C:\Program Files\QlikView\qv.exe",outputqvw,varstring,'/l'])
		else:
			subprocess.Popen(["C:\Program Files\QlikView\qv.exe",outputqvw,varstring])	

	print('Finished!')

def subbify_comandline():
	"""Command line version of subbify.

	This is installed as a command line tool by setuptools as QVSubbify.

	Usage::

		> QVSubbify "MyQlikViewScript.qvs"

	"""
	args = sys.argv
	print('Args:' + str(args))
	pathname = os.path.abspath(sys.argv[1])
	if '-f' in sys.argv:
		reload_after = 'f'
	else:
		reload_after = 's'
	subbify(pathname,open_after = True, reload_after = reload_after)

