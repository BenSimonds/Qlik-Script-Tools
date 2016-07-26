from qvstools.blocks import *

#qvs = r'C:\Users\ben.simonds\Documents\TFL_Minimal\ETL\ETLTubeData.qvs'
qvs = r"C:\Users\ben.simonds\Desktop\BetsysScript.qvs"

bl = BlockLibrary('bl')

bl.add_text_block(
	'test',
	'test',
	'test',
	qvs)

block = bl.blocks['test']

results = bl.find_referenced_files(block,'xlsx')

for r in results:
	print(r['line'],r['file'],r['text'],r['type'])