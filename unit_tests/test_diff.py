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

class TestDiff(BrdUnitBase):
    """Unit tests for the diff subcommand.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestDiff,self).setUp()
        
    def tearDown(self):
        # Call superclass's cleanup routine
        super(TestDiff,self).tearDown()

    def test_identical_trees(self):
        """Tests diff subcommand with identical trees.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ''

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
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA', 'rootB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Verify results
        self.assertEqual( scr_out, exp_out )
        
    def test_identical_files(self):
        """Tests diff subcommand with identical files.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ''

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA/TreeA/DirA/LeafA/BunchOfAs.txt', 
                                           'rootA/LeafB/BunchOfAs.txt'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Verify results
        self.assertEqual( scr_out, exp_out )

    def test_file_vs_dir(self):
        """Tests diff subcommand with file and directory.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = 'rootA/TreeA/DirA/LeafA/BunchOfAs.txt is a file.\n' + \
            'rootA/LeafB is a directory.\n'

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA/TreeA/DirA/LeafA/BunchOfAs.txt', 
                                           'rootA/LeafB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Verify results
        self.assertEqual( scr_out, exp_out )
        
    def test_dissimilar_trees(self):
        """Tests diff subcommand with two dissimilar trees.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ['Only in rootA/LeafB: BunchOfAs.txt',
                   'Only in rootA/LeafB: BunchOfBs.txt',
                   'Only in rootA/TreeA: DirA', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA/TreeA', 'rootA/LeafB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_output_option(self):
        """Tests diff subcommand with --output option.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        out_file = 'test_output.txt'
        exp_out = ['Only in rootA/LeafB: BunchOfAs.txt\n',
                   'Only in rootA/LeafB: BunchOfBs.txt\n',
                   'Only in rootA/TreeA: DirA\n']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Try --output option
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           '--output', out_file,
                                           'rootA/TreeA', 'rootA/LeafB'], 
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

        # Try -o option.
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           '-o', out_file,
                                           'rootA/TreeA', 'rootA/LeafB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        with open(out_file, 'rt') as f:
            scr_lines = f.readlines()

        # Verify results
        self.assertEqual( scr_out, '' )

        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

        # Remove output file
        os.unlink( out_file )
        
    def test_root_prefix(self):
        """Tests diff subcommand with --root-prefix option.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ['Only in LeafB: BunchOfAs.txt',
                   'Only in LeafB: BunchOfBs.txt',
                   'Only in TreeA: DirA', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           '--root-prefix', 'rootA',
                                           'TreeA', 'LeafB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_use_root(self):
        """Tests diff subcommand with --use-root option.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ['Only in my_temp/LeafB: BunchOfAs.txt',
                   'Only in my_temp/LeafB: BunchOfBs.txt',
                   'Only in my_temp/TreeA: DirA', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           '--use-root', 'rootA', 
                                           'my_temp/TreeA', 'my_temp/LeafB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_invalid_target_left(self):
        """Tests diff subcommand with an invalid target on left and a valid
        target on right.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ["'rootA/TreeB' not in database!"]

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA/TreeB', 'rootA/LeafB'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        tmp_scr_lines = scr_out.split('\n')
        scr_lines = []
        for idx in range(0, len(tmp_scr_lines)):
            find_result = tmp_scr_lines[idx].find("] ")
            if 0 < len(tmp_scr_lines[idx]) and 0 < find_result:
                scr_lines.append( tmp_scr_lines[idx][find_result + 2:] )

        # Verify results
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    def test_invalid_target_right(self):
        """Tests diff subcommand with a valid target on left and an invalid
        target on right.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ["'rootA/LeafA' not in database!"]

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA/TreeA', 'rootA/LeafA'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        tmp_scr_lines = scr_out.split('\n')
        scr_lines = []
        for idx in range(0, len(tmp_scr_lines)):
            find_result = tmp_scr_lines[idx].find("] ")
            if 0 < len(tmp_scr_lines[idx]) and 0 < find_result:
                scr_lines.append( tmp_scr_lines[idx][find_result + 2:] )

        # Verify results
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    def test_invalid_target_both(self):
        """Tests diff subcommand with two invalid targets.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ["'rootA/TreeB' not in database!",
                   "'rootA/LeafA' not in database!"]

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( mod_time, check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Diff targets
        scr_out = subprocess.check_output([self.script_name, 'diff', 
                                           'rootA/TreeB', 'rootA/LeafA'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        tmp_scr_lines = scr_out.split('\n')
        scr_lines = []
        for idx in range(0, len(tmp_scr_lines)):
            find_result = tmp_scr_lines[idx].find("] ")
            if 0 < len(tmp_scr_lines[idx]) and 0 < find_result:
                scr_lines.append( tmp_scr_lines[idx][find_result + 2:] )

        # Verify results
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    # def test_file_target_wildcard(self):
    #     """Tests diff subcommand with wildcards.
    #     """

    #     mod_time = int(time.time())
    #     check_time = datetime.datetime.fromtimestamp(mod_time)

    #     # Call open_db, which should create db and its tables
    #     self.open_db( self.default_db, False )

    #     # Populate the database with schema 1.
    #     exp_data = self.get_schema_1( mod_time, check_time )
    #     self.populate_db_from_tree( exp_data )
    #     self.conn.close()

    #     # Attempt to remove targets.
    #     scr_out = subprocess.check_output([self.script_name, 'rm', 
    #                                        'rootA/*.txt'], 
    #                                       universal_newlines=True)

    #     # Remove targets from expected contents
    #     del(exp_data['roots']['rootA']['children']['BunchOfCs.txt'])

    #     # Reopen database
    #     self.open_db( self.default_db, False )
    #     cursor = self.conn.cursor()

    #     # Build a tree data structure from the current database contents.
    #     cur_data = self.build_tree_data_from_db( cursor )

    #     # Strip out contents field from all file entries and Name from the
    #     # top-level before comparing
    #     exp_data = self.strip_fields( exp_data, 'contents' )
    #     cur_data = self.strip_fields( cur_data, 'contents' )
    #     del(exp_data['Name'])
    #     del(cur_data['Name'])

    #     diff_results = self.diff_trees( exp_data, cur_data)
        
    #     # Verify results
    #     self.assertEqual( diff_results['left'], None)
    #     self.assertEqual( diff_results['right'], None)
    #     self.assertNotEqual( len( diff_results['common']['roots'] ), 0)

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
