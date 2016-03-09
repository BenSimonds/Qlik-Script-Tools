from qvstools.blocks import *

bl = BlockLibrary('Subbify')

bl.add_text_block('Subbify','Full script for subbify','SCRIPT','blocks/source/Subbify_Full.qvs')

bl.split_block_tabs(bl.blocks['Subbify'])
print(bl.blocks.keys())
for b in [b for b in bl.blocks.values() if b.type =='TAB']:
	print(b.name)
	bl.block_to_xml(b)
print(bl.blocks.keys())