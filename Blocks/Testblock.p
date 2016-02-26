(iqvstools.blocks
Block
p0
(dp1
S'text'
p2
S"\n//(@0,'Test Replace definition 0')\n//(@1,'Test Replace definition 1')\n//(@2,'Test Replace definition 2')\n\n///$tab Main\nSET ThousandSep=',';\nSET DecimalSep='.';\nSET MoneyThousandSep=',';\nSET MoneyDecimalSep='.';\nSET MoneyFormat='\xc2\xa3#,##0.00;-\xc2\xa3#,##0.00';\nSET TimeFormat='hh:mm:ss';\nSET DateFormat='DD/MM/YYYY';\nSET TimestampFormat='DD/MM/YYYY hh:mm:ss[.fff]';\nSET MonthNames='Jan;Feb;Mar;Apr;May;Jun;Jul;Aug;Sep;Oct;Nov;Dec';\nSET DayNames='Mon;Tue;Wed;Thu;Fri;Sat;Sun';\n\n//Test Replace Methods Here: @0 @1 @2 \n"
p3
sS'replacelist'
p4
(lp5
(S'@0'
p6
S'Test Replace definition 0'
p7
tp8
a(S'@1'
p9
S'Test Replace definition 1'
p10
tp11
a(S'@2'
p12
S'Test Replace definition 2'
p13
tp14
asS'type'
p15
S'BlockType'
p16
sS'name'
p17
S'Testblock'
p18
sS'description'
p19
S'Test of Main block'
p20
sb.