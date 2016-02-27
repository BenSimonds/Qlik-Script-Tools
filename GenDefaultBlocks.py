#Generate my default blocks.

import os
from qvstools.blocks import *


bl = BlockLibrary('defs')

bl.add_text_block('Default_Start','The default qlik start section with system variables etc.','TAB','blocks/source/tab_Main.qvs')
bl.add_text_block('Default_Sub_Meta','Subroutine for getting metadata about a table. Called after load.','SUB','blocks/source/sub_Metadata.qvs')
bl.add_text_block('Default_Init_Meta','Block to run before loading a table.','BLOCK','blocks/source/block_InitMeta.qvs')
bl.add_text_block('Default_Call_Meta','Block to run after loading a table,  takes the name of the table as the replacelist.','BLOCK','blocks/source/block_CallMeta.qvs')

for b in bl.blocks:
	bl.pickle_block(bl.blocks[b])






