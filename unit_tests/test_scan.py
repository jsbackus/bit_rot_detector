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

class TestScan(BrdUnitBase):
    """Unit tests for the scan subcommand.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestScan,self).setUp()
        
    def tearDown(self):
        # Call superclass's cleanup routine
        super(TestScan,self).tearDown()

    def test_new_root(self):
        """Tests scan subcommand with a single new root.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Build tree with schema 1
        exp_data = self.get_schema_1( mod_time, check_time )
        self.build_tree( exp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           'test_tree/rootA'],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Get contents of database
        got_data = self.build_tree_data_from_db( self.conn.cursor() )
        self.conn.close()

        # Tweak root of expect data and then make sure they're the same
        tmp_data = exp_data['roots']['rootA']
        del(exp_data['roots']['rootA'])
        exp_data['roots']['test_tree/rootA'] = tmp_data
        results = self.diff_trees( exp_data, got_data )
        print(str(results))

        # Verify results 
        self.assertEqual( len(results['left']), 0 )
        self.assertEqual( len(results['right']), 0 )
        self.assertNotEqual( len(results['common']), 0 )
        
    # def test_dissimilar_trees(self):
    #     """Tests scan subcommand with dissimilar trees.
    #     """

    #     mod_time = int(time.time())
    #     check_time = datetime.datetime.fromtimestamp(mod_time)
    #     exp_out = ['']

    #     # Call open_db, which should create db and its tables
    #     self.open_db( self.default_db, False )

    #     # Populate the database with schema 1.
    #     self.populate_db_from_tree( 
    #         self.get_schema_1( str(mod_time), check_time ) )
    #     # Populate the database with schema 3.
    #     self.populate_db_from_tree( 
    #         self.get_schema_3( str(mod_time), check_time ) )
    #     self.conn.close()

    #     # Check targets
    #     scr_out = subprocess.check_output([self.script_name, 'scan'], 
    #                                       stderr=subprocess.STDOUT,
    #                                       universal_newlines=True)

    #     scr_lines = scr_out.split('\n')

    #     # Verify results 
    #     self.assertEqual( len(scr_lines), len(exp_out) )
    #     for exp_line in exp_out:
    #         self.assertTrue( exp_line in scr_lines )
        
# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
