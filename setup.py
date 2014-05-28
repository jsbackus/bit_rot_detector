#!/usr/bin/env python3

from distutils.core import setup, Extension
import gzip

# Force Gzip of the man page
# See gzip module
with open('brd.1', 'rb') as fin:
    with gzip.open('brd.1.gz', 'wb') as fout:
        fout.writelines( fin )

setup( name='Bit Rot Detector',
       version='1',
       description='Tool for checking files for damage due to aging.',
       author='Jeff Backus',
       author_email='jeff.backus@gmail.com',
       url='http://github.com/jsbackus/bit_rot_detector',
       license='GPLv2',
       platforms='win32,linux,osx',
       scripts=['brd'],
       long_description='To Do',
       data_files=[('share/man/man1', ['brd.1.gz'])],
   )
