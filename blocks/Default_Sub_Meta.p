(iqvstools.blocks
Block
p0
(dp1
S'text'
p2
S"\n///$tab SUB Meta\nSub Meta (vTable)\n\nlet vSubEnd = now();\nlet vSubTime = Interval('$(vSubStart)' - '$(vSubEnd)');\n\nMetadata:\nLoad\n\t'$(vSubStart)'\t\t\tas Meta_Start\n,\t'$(vSubEnd)'\t\t\tas Meta_End\n,\t'$(vSubTime)'\t\t\tas Meta_Time\n,\t'$(vTable)'\t\t\t\tas Meta_Table\n,\tNoOfRows('$(vTable)') \tas Meta_NoOfRows\n,\tNoOfFields('$(vTable)')\tas Meta_NoOfCols\n,\t'ALL_META'\t\t\t\tas ALL_META\nAutoGenerate 1;\n\nend sub;\n\n//Set vSubStart Now, in case the user forgets to set it later.\nlet vSubStart = now();\n"
p3
sS'replacelist'
p4
(lp5
sS'type'
p6
S'SUB'
p7
sS'name'
p8
S'Default_Sub_Meta'
p9
sS'description'
p10
S'Subroutine for getting metadata about a table. Called after load.'
p11
sb.