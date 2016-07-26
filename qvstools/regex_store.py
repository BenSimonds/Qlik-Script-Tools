"""Here we just store some shared regex searches"""
import re

patterns = {
	# First attempt at matching valid windows filepaths. These work quite well actually.
	#(?:\s|^)\[((?:[A-Z]:|\\\\|(?:\.\.\\)+)[\\\w \-_]+)\.(qvd|xls[xm]?|csv|qvx)\]|(?:\s|^)((?:[A-Z]:|\\\\|(?:\.\.\\)+)[\\\w \-_]+)\.(qvd|xls[xm]?|csv|qvx)
	'filestring1': r"((?:[A-Z]:|\\\\|//|(?:\.\.\\|\.\./)*)[/\\\w\-_\. ]+)", #Has spaces
	'filestring2': r"((?:[A-Z]:|\\\\|//|(?:\.\.\\|\.\./)*)[/\\\w\-_\.]+)", #No spaces

	# Improved searches for files based on from ... (options) or into ... (options)
	# Matches "from" statements for qvds:
	'from_qvd' : r"from[\s\n]*\[?(.*?)\]?[\s\n]*\((?:qvd)\)",

	# To match *any* valid from statement, we need something between from and then followed by an open bracket
	# followed by any valid qlik format specifier, with optional whitespace.
	'from_any': r"from[\s\n]*\[?(.*?)\]?[\s\n]*\((?:ansi|oem|mac|UTF-8|Unicode|txt|fix|dif|biff|ooxml|html|xml|qvd|delimiter is|no eof|embedded labels|explicit labels|no labels|table is|header is |header is|comment is|record is|no quotes|msq|filters)",

	# Matching any valid into statement is easier since there are only two format specifiers: (txt) and (qvd).
	'into_any': r"into[\s\n]*(.*?)[\s\n]*\((?:txt|qvd)\)"
}

searches = {
    # First functional version of a file finder for log files.
    'filesearchstring1':re.compile(r"(?:\s|\[|^)((?:\.\.|\\\\|\\)*[\\\w \-_]+)\.(qvd|xls[xm]?)\]?", flags=re.I),
    # Second attempt, differentiates between "[strings with spaces]" and "stringswithoutspaces"
    'filesearchstring2':re.compile(r"(?:\s|^)"+patterns['filestring2'] +"\.(qvd|xls[xm]?|csv|qvx)|(?:\s|^)\["+patterns['filestring1'] +"\.(qvd|xls[xm]?|csv|qvx)\]", flags=re.I),
    # Store search string, matches store x into y statements.
    'store_statement':re.compile(r"store\s\[?[\w\s\-_\.]*\]?\sinto", flags=re.I),
    # Directory search string, matches Directory Path/To/Directory
    'directory_statement':re.compile(r"directory " + patterns['filestring1'] + r"|directory \[" + patterns['filestring2'] + r"\]", flags=re.I),
    # From QVD Statement
    'from_qvd':re.compile(patterns['from_qvd'],re.I),
    # From Any Statement
    'from_any':re.compile(patterns['from_any'], re.I),
    # Into Any Statement
    'into_any':re.compile(patterns['into_any'], re.I)
}
