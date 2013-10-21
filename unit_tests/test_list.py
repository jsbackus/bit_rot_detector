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

        exp_out = os.linesep.join( ( 'rootA:', '    LeafB/', '    TreeA/',
                                     '    BunchOfCs.txt', '',
                                     '3 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1() )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA'])

        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_file_target(self):
        """Tests list subcommand with one file target.
        """

        mod_time = int(time.time())
        exp_out = os.linesep.join( ( 'Files matching rootA/BunchOfCs.txt:', '',
                                     'BunchOfCs.txt:', '    ID: 1',
                                     '    Last Modified: ' + str(
                    datetime.datetime.fromtimestamp(mod_time) ),
                                     '    Fingerprint: 0xff3785f53b503b7adb7e' +
                                     '7a3b9eeef255eac0e276',
                                     '    Size: 257 bytes', '',
                                     '1 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA/BunchOfCs.txt'])
        # Verify output
        self.assertEqual( scr_out, exp_out )

    def test_multiple_targets(self):
        """Tests list subcommand with multiple targets.
        """

        mod_time = int(time.time())
        exp_out = os.linesep.join( ( 'Files matching rootA/BunchOfCs.txt:', '',
                                     'BunchOfCs.txt:', '    ID: 1',
                                     '    Last Modified: ' + str(
                    datetime.datetime.fromtimestamp(mod_time) ),
                                     '    Fingerprint: 0xff3785f53b503b7adb7e' +
                                     '7a3b9eeef255eac0e276',
                                     '    Size: 257 bytes', '',
                                     '1 entries listed.', '', 
                                     'rootA/LeafB:', '    BunchOfAs.txt', 
                                     '    BunchOfBs.txt', '', 
                                     '2 entries listed.', '', '' ) )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( self.get_schema_1( mod_time ) )
        self.conn.close()

        # Attempt to list contents
        scr_out = subprocess.check_output([self.script_name, 'list', 
                                           'rootA/BunchOfCs.txt', 
                                           'rootA/LeafB'])
        # Verify output
        self.assertEqual( scr_out, exp_out )

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
