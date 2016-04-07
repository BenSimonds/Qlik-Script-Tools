"""Here we just store some shared regex searches"""
import re

filestring1 = ''

searches = {
    #First functional version of a file finder for log files.
    'filesearchstring1':re.compile(r"(?:\s|\[|^)((?:\.\.|\\\\|\\)*[\\\w \-_]+)\.(qvd|xls[xm]?)\]?"),
    #Second attempt, differentiates between "[strings with spaces]" and "stringswithoutspaces"
    'filesearchstring2':re.compile(r"(?:\s|^)\[((?:\.\.|\\\\|\\)*[\\\w \-_]+)\.(qvd|xls[xm]?|csv|qvx)\]|(?:\s|^)((?:\.\.|\\\\|\\)*[\\\w\-_]+)\.(qvd|xls[xm]?|csv|qvx)"),
    #Store search string, matches store x into y statements.
    'store_statement':re.compile(r"store\s\[?[\w\s]*\]?\sinto")
    #Directory search string, matches Directory Path/To/Directory
    'directory_statement':re.compile(r"directory  ")
}
