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

from __future__ import unicode_literals

import os
import subprocess
import unittest
import datetime
import time

from brd_unit_base import BrdUnitBase

# Import brd in order to use some of its functions
# Note: we're expecting brd_unit_base to take care of path stuff
import brd

class TestDupeFiles(BrdUnitBase):
    """Unit tests for the dupe_files subcommand.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestDupeFiles,self).setUp()
        
    def tearDown(self):
        # Call superclass's cleanup routine
        super(TestDupeFiles,self).tearDown()

    def test_identical_trees(self):
        """Tests dupe_files subcommand with identical trees.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = \
            ['4 files with Fingerprint ' +
             '0x1a0372738bb5b4b8360b47c4504a27e6f4811493:',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfAs.txt',
             '    [rootA]/LeafB/BunchOfAs.txt',
             '    [rootB]/TreeA/DirA/LeafA/BunchOfAs.txt',
             '    [rootB]/LeafB/BunchOfAs.txt',
             '4 files with Fingerprint ' +
             '0xfa75bf047f45891daee8f1fa4cd2bf58876770a5:',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfBs.txt',
             '    [rootA]/LeafB/BunchOfBs.txt',
             '    [rootB]/TreeA/DirA/LeafA/BunchOfBs.txt',
             '    [rootB]/LeafB/BunchOfBs.txt',
             '2 files with Fingerprint ' +
             '0xb145bb8710c9b6624bb46631eecc3bbcc335d0ab:',
             '    [rootA]/BunchOfCs.txt',
             '    [rootB]/BunchOfCs.txt', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1
        self.populate_db_from_tree( 
            self.get_schema_1( mod_time, check_time ) )
        # Append another schema 1 with a new root name
        self.populate_db_from_tree( 
            self.get_schema_1( mod_time, check_time, 
                               root_name = 'rootB', first_file_id=6,
                               first_dir_id=6) )
        self.conn.close()

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'dupe_files'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_dissimilar_trees(self):
        """Tests dupe_files subcommand with dissimilar trees.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = \
            ['2 files with Fingerprint ' +
             '0x1a0372738bb5b4b8360b47c4504a27e6f4811493:',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfAs.txt',
             '    [rootA]/LeafB/BunchOfAs.txt',
             '2 files with Fingerprint ' +
             '0xfa75bf047f45891daee8f1fa4cd2bf58876770a5:',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfBs.txt',
             '    [rootA]/LeafB/BunchOfBs.txt', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( 
            self.get_schema_1( mod_time, check_time ) )
        # Populate the database with schema 3.
        self.populate_db_from_tree( 
            self.get_schema_3( mod_time, check_time ) )
        self.conn.close()

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'dupe_files'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_single_tree_with_duplicates(self):
        """Tests dupe_files subcommand with a single tree that has duplicate
        files.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = \
            ['2 files with Fingerprint ' +
             '0x1a0372738bb5b4b8360b47c4504a27e6f4811493:',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfAs.txt',
             '    [rootA]/LeafB/BunchOfAs.txt',
             '2 files with Fingerprint ' +
             '0xfa75bf047f45891daee8f1fa4cd2bf58876770a5:',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfBs.txt',
             '    [rootA]/LeafB/BunchOfBs.txt', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'dupe_files'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_single_tree_without_duplicates(self):
        """Tests dupe_files subcommand with a single tree that does not have 
        duplicate files.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ''

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_3( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'dupe_files'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Verify results 
        self.assertEqual( scr_out, exp_out )
        
    def test_output_option(self):
        """Tests dupe_files subcommand with --output option.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        out_file = 'test_output.txt'
        exp_out = \
            ['2 files with Fingerprint ' +
             '0x1a0372738bb5b4b8360b47c4504a27e6f4811493:\n',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfAs.txt\n',
             '    [rootA]/LeafB/BunchOfAs.txt\n',
             '2 files with Fingerprint ' +
             '0xfa75bf047f45891daee8f1fa4cd2bf58876770a5:\n',
             '    [rootA]/TreeA/DirA/LeafA/BunchOfBs.txt\n',
             '    [rootA]/LeafB/BunchOfBs.txt\n']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check --output
        scr_out = subprocess.check_output([self.script_name, 'dupe_files', 
                                           '--output', out_file], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        with open(out_file, 'rt') as f:
            scr_lines = f.readlines()

        # Verify results
        self.assertEqual( scr_out, '' )

        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

        # Remove output file and try again with -o option
        os.unlink( out_file )

        # Check -o
        scr_out = subprocess.check_output([self.script_name, 'dupe_files', 
                                           '-o', out_file], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        with open(out_file, 'rt') as f:
            scr_lines = f.readlines()

        # Verify results
        self.assertEqual( scr_out, '' )

        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

        # Clean up
        os.unlink( out_file )
        
# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
