#!/usr/bin/env python3
#    brd - scans directories and files for damage due to decay of medium.
#    Copyright (C) 2013 Jeff Backus <jeff.backus@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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

setup( name='bit_rot_detector',
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
                   ('share/doc/bit_rot_detector', ['README', 'LICENSE'])],
       cmdclass=cmdclass,
   )
