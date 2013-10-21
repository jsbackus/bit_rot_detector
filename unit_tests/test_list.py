from __future__ import unicode_literals

import os
import subprocess
import unittest

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

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
