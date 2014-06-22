#!/usr/bin/env python3

from distutils.core import setup, Extension
from distutils.command.build import build
import gzip

class my_build(build):
    def run(self):
        # Gzip the man page
        # See gzip module
        with open('brd.1', 'rb') as fin:
            with gzip.open('brd.1.gz', 'wb') as fout:
                fout.writelines( fin )
        
        # Run normal build
        build.run(self)

cmdclass = {}
cmdclass['build'] = my_build

setup( name='brd',
       version='1',
       description='Tool for checking files for damage due to aging.',
       author='Jeff Backus',
       author_email='jeff.backus@gmail.com',
       url='http://github.com/jsbackus/bit_rot_detector',
       license='GPLv2',
       platforms='win32,linux,osx',
       scripts=['brd'],
       long_description='BRD is a tool to scan a directory tree and check ' +
       'each file for corruption caused by damage to the physical storage ' +
       'medium or by damage from malicious programs. Files are fingerprinted ' +
       'using the SHA-1 algorithm. File fingerprints, sizes, and modification' +
       ' times are stored in a SQLite database.',
       data_files=[('share/man/man1', ['brd.1.gz']),
                   ('share/doc/brd', ['README', 'LICENSE'])],
       cmdclass=cmdclass,
   )
