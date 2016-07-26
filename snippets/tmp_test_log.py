import qvstools.log as lg
from qvstools.regex_store import *
import re

logfile = r"C:\Users\ben.simonds.KEYRUSCORP\Repositories\qlik-script-tools\qvstools\tests\testdata\DepsGraph3.qvw.log"
scriptfile = r"C:\Users\ben.simonds.KEYRUSCORP\Repositories\qlik-script-tools\qvstools\tests\testdata\ETLTubeData.qvs"

with open(scriptfile,'r',encoding = 'utf8') as lf:
	fulltext = lf.read()
	#print(fulltext, len(fulltext))
	for match in set(re.finditer(patterns['from_any'], fulltext, re.I)):
		print('-------------------')
		print(match.group(1))

print('>>>>>>>>>>>>>>')

print(lg.get_referenced_files(logfile,search='*'))