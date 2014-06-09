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

class TestList(BrdUnitBase):
    """Unit tests for the list subcommand.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestList,self).setUp()
        
    def tearDown(self):
        # Call superclass's cleanup routine
        super(TestList,self).tearDown()

    def test_dir_target(self):
        """Tests list subcommand with one directory target.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( 'rootA:', '    TreeA/', '    LeafB/',
                                     '    BunchOfCs.txt', '',
                                     '3 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA'], universal_newlines=True)

        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_file_target(self):
        """Tests list subcommand with one file target.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( "Files matching 'rootA/BunchOfCs.txt':",
                                     '', 'BunchOfCs.txt:', '    ID: 1',
                                     '    Last Modified: ' + str( mod_time ),
                                     '    Fingerprint: 0x' +
                                     'b145bb8710c9b6624bb46631eecc3bbcc335d0ab',
                                     '    Size: 257 bytes', '',
                                     '1 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA/BunchOfCs.txt'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_multiple_targets(self):
        """Tests list subcommand with multiple targets.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( "Files matching 'rootA/BunchOfCs.txt':",
                                     '', 'BunchOfCs.txt:', '    ID: 1',
                                     '    Last Modified: ' + str( mod_time ),
                                     '    Fingerprint: 0x' +
                                     'b145bb8710c9b6624bb46631eecc3bbcc335d0ab',
                                     '    Size: 257 bytes', '',
                                     '1 entries listed.', '', 
                                     'rootA/LeafB:','    BunchOfBs.txt',
                                     '    BunchOfAs.txt', '', 
                                     '2 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA/BunchOfCs.txt', 
                                           'rootA/LeafB'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_invalid_target(self):
        """Tests list subcommand with an invalid target.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( 'rootA/BunchOfDs.txt is not in database.',
                                     '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA/BunchOfDs.txt'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_file_target_wildcard(self):
        """Tests list subcommand with multiple file targets, using wildcards.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( "Files matching 'rootA/LeafB/*.txt':", '',
                                     'BunchOfBs.txt:', '    ID: 2',
                                     '    Last Modified: ' + str( mod_time ),
                                     '    Fingerprint: 0xfa75bf047f45891daee8' +
                                     'f1fa4cd2bf58876770a5',
                                     '    Size: 257 bytes', 
                                     'BunchOfAs.txt:', '    ID: 3',
                                     '    Last Modified: ' + str( mod_time ),
                                     '    Fingerprint: 0x1a0372738bb5b4b8360b' +
                                     '47c4504a27e6f4811493',
                                     '    Size: 257 bytes', '',
                                     '2 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA/LeafB/*.txt'], 
                                          universal_newlines=True)

        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_use_root(self):
        """Tests list subcommand with one file target and the --use-root option.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( "Files matching 'my_temp/BunchOfCs.txt':", 
                                     '', 'BunchOfCs.txt:', '    ID: 1',
                                     '    Last Modified: ' + str( mod_time ),
                                     '    Fingerprint: 0x' +
                                     'b145bb8710c9b6624bb46631eecc3bbcc335d0ab',
                                     '    Size: 257 bytes', '',
                                     '1 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           '--use-root', 'rootA', 
                                           'my_temp/BunchOfCs.txt'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_root_prefix(self):
        """Tests list subcommand with one file target and the --root-prefix 
        option.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( "Files matching 'BunchOfCs.txt':", 
                                     '', 'BunchOfCs.txt:', '    ID: 1',
                                     '    Last Modified: ' + str( mod_time ),
                                     '    Fingerprint: 0x' +
                                     'b145bb8710c9b6624bb46631eecc3bbcc335d0ab',
                                     '    Size: 257 bytes', '',
                                     '1 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           '--root-prefix', 'rootA', 
                                           'BunchOfCs.txt'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_minimal(self):
        """Tests list subcommand --minimal option
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( 'TreeA/', 'LeafB/', 'BunchOfCs.txt', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents with --minimal
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           '--minimal', 'rootA'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

        # Attempt to list contents with -m
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           '-m', 'rootA'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_expanded(self):
        """Tests list subcommand --expanded option
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = os.linesep.join( ( 'rootA:', '    [INFO]', '        ID: 1',
                                     '        Parent ID: -1', 
                                     '        Last Checked: ' + str( mod_time ),
                                     '    [Subdirectories]',
                                     '        TreeA/ (2)',
                                     '        LeafB/ (3)',
                                     '    [Files]', '        BunchOfCs.txt (1)',
                                     '', '3 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time, check_time ) )
        self.conn.close()

        # Attempt to list contents with --expanded
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           '--expanded', 'rootA'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )

        # Attempt to list contents with -e
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           '-e', 'rootA'], 
                                          universal_newlines=True)
        # Verify output
        self.assertEqual( scr_out, exp_out )


# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
