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

import unittest
import os

from brd_unit_base import BrdUnitBase

# Import brd in order to use some of its functions
# Note: we're expecting brd_unit_base to take care of path stuff
import brd

class TestMisc(BrdUnitBase):
    """Miscellaneous unit tests not related to any subcommands.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestMisc,self).setUp()

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

        # Make sure database doesn't exist. If it does, clobber it.
        if os.path.exists( db_url ):
            os.remove( db_url )

        # Call open_db, which should create db and its tables
        self.conn = brd.open_db( db_url )

        # Verify that file exists
        self.assertTrue( os.path.exists( db_url ) )

        # Verify that files table exist
        self.assertTrue( self.find_table( self.table_names['files'] ) )
        
        # Verify that dirs table exists
        self.assertTrue( self.find_table( self.table_names['dirs'] ) )

#    def test_pfft(self):
#        self.build_tree( self.get_schema_1() )

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
