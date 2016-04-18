"""Tools for helping with text files, encodings etc."""
import sys

known_encodings = { #Contains known encodings for different file types:
	'qvd':'cp1252',
	'log':['utf-16','utf-8'],
	'prj_xml':'utf-8-sig',
	'block_xml':'utf-8',
	'block_qvs':'utf-8',
	'txt':'utf-8'
}

#Cant get the below to print to a single line at the moment...
def print_progress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 30):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterations  - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    print('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix),flush=False)
    if iteration == total:
        print("\n")