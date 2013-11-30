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

    def test_dir_target(self):
        """Tests diff subcommand with one directory target.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target subtree.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           'rootA/TreeA'], 
                                          universal_newlines=True)

        # Remove target subtree from expected contents
        del(exp_data['roots']['rootA']['children']['TreeA'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        
    def test_file_target(self):
        """Tests diff subcommand with one file target.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target file.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           'rootA/LeafB/BunchOfAs.txt'], 
                                          universal_newlines=True)

        # Remove target file from expected contents
        del(exp_data['roots']['rootA']['children']['LeafB']['children']\
            ['BunchOfAs.txt'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)

    def test_root_target(self):
        """Tests diff subcommand with one root target.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_2( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target subtree.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           'rootA'], 
                                          universal_newlines=True)

        # Remove target subtree from expected contents
        del(exp_data['roots']['rootA'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )
 
        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)

        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        
    def test_multiple_targets(self):
        """Tests diff subcommand with multiple targets.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove targets.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           'rootA/TreeA', 
                                           'rootA/LeafB/BunchOfAs.txt'], 
                                          universal_newlines=True)

        # Remove targets from expected contents
        del(exp_data['roots']['rootA']['children']['TreeA'])
        del(exp_data['roots']['rootA']['children']['LeafB']['children']\
            ['BunchOfAs.txt'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        
    def test_use_root(self):
        """Tests diff subcommand with one file target and the --use-root 
        option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target subtree.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           '--use-root', 'rootA',
                                           'my_temp/TreeA'], 
                                          universal_newlines=True)

        # Remove target subtree from expected contents
        del(exp_data['roots']['rootA']['children']['TreeA'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        
    def test_root_prefix(self):
        """Tests diff subcommand with one file target and the --root-prefix 
        option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target subtree.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           '--root-prefix', 'rootA',
                                           'TreeA'], 
                                          universal_newlines=True)

        # Remove target subtree from expected contents
        del(exp_data['roots']['rootA']['children']['TreeA'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        
    def test_dry_run(self):
        """Tests diff subcommand with --dry-run option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target subtree.
        scr_out = subprocess.check_output([self.script_name, 'rm',
                                           '--dry-run', 'rootA/TreeA'], 
                                          universal_newlines=True)

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        
    def test_invalid_target(self):
        """Tests diff subcommand with an invalid target.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        exp_out = "Target 'rootB/TreeA' not in database."

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove target subtree.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           'rootB/TreeA'],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)
        self.assertNotEqual( scr_out.find( exp_out ), -1 )
        
    def test_file_target_wildcard(self):
        """Tests diff subcommand with wildcards.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_1( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Attempt to remove targets.
        scr_out = subprocess.check_output([self.script_name, 'rm', 
                                           'rootA/*.txt'], 
                                          universal_newlines=True)

        # Remove targets from expected contents
        del(exp_data['roots']['rootA']['children']['BunchOfCs.txt'])

        # Reopen database
        self.open_db( self.default_db, False )
        cursor = self.conn.cursor()

        # Build a tree data structure from the current database contents.
        cur_data = self.build_tree_data_from_db( cursor )

        # Strip out contents field from all file entries and Name from the
        # top-level before comparing
        exp_data = self.strip_fields( exp_data, 'contents' )
        cur_data = self.strip_fields( cur_data, 'contents' )
        del(exp_data['Name'])
        del(cur_data['Name'])

        diff_results = self.diff_trees( exp_data, cur_data)
        
        # Verify results
        self.assertEqual( diff_results['left'], None)
        self.assertEqual( diff_results['right'], None)
        self.assertNotEqual( len( diff_results['common']['roots'] ), 0)

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
