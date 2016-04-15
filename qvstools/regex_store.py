"""Here we just store some shared regex searches"""
import re

#(?:\s|^)\[((?:[A-Z]:|\\\\|(?:\.\.\\)+)[\\\w \-_]+)\.(qvd|xls[xm]?|csv|qvx)\]|(?:\s|^)((?:[A-Z]:|\\\\|(?:\.\.\\)+)[\\\w \-_]+)\.(qvd|xls[xm]?|csv|qvx)
filestring1 = r"((?:[A-Z]:|\\\\|//|(?:\.\.\\|\.\./)*)[/\\\w\-_\. ]+)" #Has spaces
filestring2 = r"((?:[A-Z]:|\\\\|//|(?:\.\.\\|\.\./)*)[/\\\w\-_\.]+)"  #No spaces


searches = {
    #First functional version of a file finder for log files.
    'filesearchstring1':re.compile(r"(?:\s|\[|^)((?:\.\.|\\\\|\\)*[\\\w \-_]+)\.(qvd|xls[xm]?)\]?", flags=re.I),
    #Second attempt, differentiates between "[strings with spaces]" and "stringswithoutspaces"
    'filesearchstring2':re.compile(r"(?:\s|^)"+filestring2+"\.(qvd|xls[xm]?|csv|qvx)|(?:\s|^)\["+filestring1+"\.(qvd|xls[xm]?|csv|qvx)\]", flags=re.I),
    #Store search string, matches store x into y statements.
    'store_statement':re.compile(r"store\s\[?[\w\s\-_\.]*\]?\sinto", flags=re.I),
    #Directory search string, matches Directory Path/To/Directory
    'directory_statement':re.compile(r"directory " + filestring1 + r"|directory \[" + filestring2 + r"\]", flags=re.I)
}