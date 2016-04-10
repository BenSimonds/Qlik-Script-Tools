try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Tools for making Qlikview load scripts and doing other automation tasks on Qlikview projects.',
    'author': 'BenSimonds',
    'url': 'https://github.com/BenSimonds/Qlik-Script-Tools',
    'download_url': 'https://github.com/BenSimonds/Qlik-Script-Tools/archive/master.zip',
    'author_email': 'BSSimonds@gmail.com',
    'version': '0.1dev',
    'packages': ['qvstools','qvstools.tests'],
    'scripts': ['runtests.py'],
    'name': 'Qlik-Script-Tools',
    'entry_points':{
        'console_scripts':[
            'QVSubbify=qvstools.subbify:subbify_comandline',
            'QVReplaceFonts=qvstools.prj:replace_fonts_commandline'
            ]
        },
    'test_suite':'qvstools.tests',
    'include_package_data':True
}

setup(**config)