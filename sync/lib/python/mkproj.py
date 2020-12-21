import os
import shutil
import sys

templateDir = os.path.expanduser('~')
templateDir = os.path.join(templateDir,'lib','python','mkprojtemplate')
projectsDir = os.getcwd()

def makeDir( dirName ):
	if not os.path.exists( dirName ):
		os.makedirs( dirName )

if len( sys.argv ) < 2:
	print ('Usage: mkproj projName [cpp|python|cuda]')
	sys.exit(1)     

if sys.argv[1] == '--version':
	print('mkproj 1.2.2')
	print('This is free software; There is NO warranty; not even for ' 
	'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.')
	print('')
	print('Written by Behram Kapadia')
	sys.exit(0)
elif sys.argv[1] == '--help':
	print('Makes a dev project from a template.')
	print('Usage: mkproj projName [cpp|cuda|python]')
	sys.exit(0)

projName = sys.argv[1]
projRoot = os.path.join(projectsDir,projName)

if len( sys.argv ) == 2:
	projType = 'cpp'
elif len( sys.argv ) == 3:
	projType = sys.argv[2]
elif len( sys.argv ) > 3 and sys.argv[2] == '-t':
	projType = sys.argv[3]

types = ['cpp', 'cuda', 'python']

if projType not in types:
	print ('project type ' + projType + ' not found')
	sys.exit(1)

shutil.copytree( os.path.join(templateDir,projType), projRoot)