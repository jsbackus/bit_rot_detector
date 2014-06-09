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
import unittest

from brd_unit_base import BrdUnitBase

# Import brd in order to use some of its functions
# Note: we're expecting brd_unit_base to take care of path stuff
import brd

class TestCheckDB(BrdUnitBase):
    """Unit tests for the checkdb subcommand.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestCheckDB,self).setUp()
        
        # Define default fingerprint file
        self.default_fp_file = self.default_db + '.sha1'

        # Remove fingerprint file
        if os.path.exists( self.default_fp_file ):
            os.unlink( self.default_fp_file )

    def tearDown(self):
        # Remove fingerprint file
        if os.path.exists( self.default_fp_file ):
            os.unlink( self.default_fp_file )

        # Call superclass's cleanup routine
        super(TestCheckDB,self).tearDown()

    def test_new_fingerprint(self):
        """Tests new fingerprint file generation.
        """

        # Call open_db, which should create db and its tables
        self.conn = brd.open_db( self.default_db )
        # Close connection
        self.conn.close()

        # Verify that the fingerprint file does not already exist
        self.assertTrue( not os.path.exists( self.default_fp_file ) )

        # Check the database
        os.system( self.script_name + ' checkdb' )

        # Verify that the fingerprint file now exists
        self.assertTrue( os.path.exists( self.default_fp_file ) )

        # Verify its contents
        expect_fp = self.calc_fingerprint( self.default_db )
        with open( self.default_fp_file, 'rt' ) as f:
            got_fp = f.readline().rstrip(os.linesep)

        self.assertEqual( expect_fp, got_fp )

    def test_update_fingerprint(self):
        """Tests fingerprinting of an updated database.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )
        # Close connection
        self.conn.close()

        # Verify that the fingerprint file does not already exist
        self.assertTrue( not os.path.exists( self.default_fp_file ) )

        # Check the database
        os.system( self.script_name + ' checkdb' )

        # Verify that the fingerprint file now exists
        self.assertTrue( os.path.exists( self.default_fp_file ) )

        # Open database again, and this time populate it with schema 1.
        self.open_db( self.default_db, False )
        self.populate_db_from_tree( self.get_schema_1() )
        self.conn.close()

        # Check the database
        os.system( self.script_name + ' checkdb' )

        # Verify its contents
        expect_fp = self.calc_fingerprint( self.default_db )
        with open( self.default_fp_file, 'rt' ) as f:
            got_fp = f.readline().rstrip(os.linesep)

        self.assertEqual( expect_fp, got_fp )

    def test_check_only(self):
        """Tests the --check-only option on an updated database.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )
        # Close connection
        self.conn.close()

        # Verify that the fingerprint file does not already exist
        self.assertTrue( not os.path.exists( self.default_fp_file ) )

        # Check the database
        os.system( self.script_name + ' checkdb' )

        # Verify that the fingerprint file now exists
        self.assertTrue( os.path.exists( self.default_fp_file ) )

        # Verify its contents
        expect_fp = self.calc_fingerprint( self.default_db )
        with open( self.default_fp_file, 'rt' ) as f:
            orig_fp = f.readline().rstrip(os.linesep)

        # Open database again, and this time populate it with schema 1.
        self.open_db( self.default_db, False )
        self.populate_db_from_tree( self.get_schema_1() )
        self.conn.close()

        # Check the database
        os.system( self.script_name + ' checkdb --check-only' )

        # Verify that the contents of the fingerprint file haven't changed.
        expect_fp = self.calc_fingerprint( self.default_db )
        with open( self.default_fp_file, 'rt' ) as f:
            new_fp = f.readline().rstrip(os.linesep)

        self.assertNotEqual( expect_fp, new_fp )
        self.assertEqual( orig_fp, new_fp )

    def test_dry_run(self):
        """Tests the --dry-run option on an updated database.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )
        # Close connection
        self.conn.close()

        # Verify that the fingerprint file does not already exist
        self.assertTrue( not os.path.exists( self.default_fp_file ) )

        # Check the database
        os.system( self.script_name + ' checkdb' )

        # Verify that the fingerprint file now exists
        self.assertTrue( os.path.exists( self.default_fp_file ) )

        # Verify its contents
        expect_fp = self.calc_fingerprint( self.default_db )
        with open( self.default_fp_file, 'rt' ) as f:
            orig_fp = f.readline().rstrip(os.linesep)

        # Open database again, and this time populate it with schema 1.
        self.open_db( self.default_db, False )
        self.populate_db_from_tree( self.get_schema_1() )
        self.conn.close()

        # Check the database
        os.system( self.script_name + ' checkdb --check-only' )

        # Verify that the contents of the fingerprint file haven't changed.
        expect_fp = self.calc_fingerprint( self.default_db )
        with open( self.default_fp_file, 'rt' ) as f:
            new_fp = f.readline().rstrip(os.linesep)

        self.assertNotEqual( expect_fp, new_fp )
        self.assertEqual( orig_fp, new_fp )

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
