from __future__ import unicode_literals
import unittest
import os
from brd_unit_base import BrdUnitBase

# Import brd in order to use some of its functions
#sys.path.insert(1, os.path.join(sys.path[0], 'site_modules'))
sys.path.insert(1, '..')
import brd

class TestMisc(BrdUnitBase):
    """Miscellaneous unit tests not related to any subcommands.
    """

    def setUp(self):
        # To do
        pass

    def test_table_names(self):
        """Verifies table names.
        """
        
        # List of expected table names
        table_names = { 'files': 'fp_files', 'dirs': 'fp_dirs', 
                'tmp_dirs' : 'tmp_dirs' }

        for entry in table_names.keys():
            self.assertEqual( brd.table_names[entry], table_names[entry] )

    def test_create_db(self):
        """Verifies that open_db() will create a new database with the 
        proper table names.
        """

        db_url = './test.db'

        # Make sure database doesn't exist
        os.remove( db_url )

        # Call open_db, which should create db and its tables
        self.conn = brd.open_db( db_url )

        # Verify that file exists

        # Verify that files table exist
        self.assertTrue( self.find_table( table_names['files'] ) )
        
        # Verify that dirs table exists
        self.assertTrue( self.find_table( table_names['dirs'] )


### Main Entry ###
if __name__ == '__main__':
    unittest.main()
