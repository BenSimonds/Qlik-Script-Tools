import qvstools.log as lg
from qvstools.regex_store import *
import re

logfile = r"..\qvstools\tests\testdata\DepsGraph3.qvw.log"
scriptfile = r"..\qvstools\tests\testdata\ETLTubeData.qvs"

with open(scriptfile,'r',encoding = 'utf8') as lf:
	fulltext = lf.read()
	#print(fulltext, len(fulltext))
	for match in set(re.finditer(patterns['from_any'], fulltext, re.I)):
		print('-------------------')
		print(match.group(1))

print('>>>>>>>>>>>>>>')

print(lg.get_referenced_files(logfile,search='*'))