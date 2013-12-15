from __future__ import unicode_literals

import os
import subprocess
import unittest
import datetime
import time
import shutil

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
        # Clean up test tree
        shutil.rmtree('test_tree')

        # Call superclass's cleanup routine
        super(TestScan,self).tearDown()
        
    def test_new_root(self):
        """Tests scan subcommand with a single new root.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time

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

        # Remove contents and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data['roots']['test_tree/rootA']['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots']['test_tree/rootA'] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_unchanged_root(self):
        """Tests scan subcommand with an existing, unchanged root.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time

        # Build tree with schema 1
        exp_data = self.get_schema_1( mod_time, check_time )
        self.build_tree( exp_data )

        # Populate the database with schema 1.
        self.populate_db_from_tree( exp_data )
        self.conn.close()

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

        # Remove contents and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data['roots']['test_tree/rootA']['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots']['test_tree/rootA'] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_changed_root(self):
        """Tests scan subcommand with an existing, changed root.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)

        # Populate the database with schema 5, modified 1 month ago.
        self.populate_db_from_tree( self.get_schema_5( mod_time, mod_time, 
                                                       'test_tree/rootA' ) )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        exp_data = self.get_schema_1( check_time, check_time, 'rootA' )
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

        # Remove contents and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data['roots']['test_tree/rootA']['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots']['test_tree/rootA'] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_existing_subtree(self):
        """Tests scan subcommand with an existing, changed subtree.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)

        # Populate the database with schema 5, modified 1 month ago.
        exp_data = self.get_schema_5( mod_time, mod_time, 'test_tree/rootA' ) 
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        post_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( post_data )

        # Replce rootA/TreeA in expected data with changed subtree
        exp_data['roots']['test_tree/rootA']['children']['TreeA'] = \
            post_data['roots']['rootA']['children']['TreeA']

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           'test_tree/rootA/TreeA'],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Get contents of database
        got_data = self.build_tree_data_from_db( self.conn.cursor() )
        self.conn.close()

        # Remove contents and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        results = self.diff_trees( exp_data['roots']['test_tree/rootA'], 
                                   got_data['roots']['test_tree/rootA'] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_multiple_roots(self):
        """Tests scan subcommand with multiple new roots.
        """

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time

        # Build schema 1 and add to expect data
        exp_data = { 'roots': dict(), 'Name': '' }
        tmp_schema = self.get_schema_1( mod_time, check_time )
        self.build_tree( tmp_schema )
        exp_data['roots']['test_tree/rootA'] = tmp_schema['roots']['rootA']

        # Build schema 3 and add to expect data
        tmp_schema = self.get_schema_3( mod_time, check_time, 
                                        rootName = 'rootB', first_file_id=6,
                                        first_dir_id=6)
        self.build_tree( tmp_schema )
        exp_data['roots']['test_tree/rootB'] = tmp_schema['roots']['rootB']

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           'test_tree/rootA', 
                                           'test_tree/rootB'],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Get contents of database
        got_data = self.build_tree_data_from_db( self.conn.cursor() )
        self.conn.close()

        # Remove contents and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID"])
        exp_data['roots']['test_tree/rootA']['Name'] = 'test_tree/rootA'
        exp_data['roots']['test_tree/rootB']['Name'] = 'test_tree/rootB'
        results = self.diff_trees( exp_data['roots'], 
                                   got_data['roots'] )

        print('Common:' +str(results['common']))
        print('Left:' +str(results['left']))
        print('Right:' +str(results['right']))

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
