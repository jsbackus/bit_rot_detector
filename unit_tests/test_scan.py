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
        target_name = os.path.join('test_tree', 'rootA')
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           target_name],
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
        target_name = os.path.join('test_tree', 'rootA')
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

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
        target_name = os.path.join('test_tree', 'rootA')
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           target_name],
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
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

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
        target_name = os.path.join('test_tree', 'rootA')
        self.populate_db_from_tree( self.get_schema_5( mod_time, mod_time, 
                                                       target_name ) )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        exp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( exp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           target_name],
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
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_corrupted_root(self):
        """Tests scan subcommand with an existing root with corrupted files.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        exp_out = ["File 'test_tree/rootA/BunchOfCs.txt' does not match " +
                   "fingerprint in database and is not newer. File could be " +
                   "damaged!",
                   "File 'test_tree/rootA/TreeA/DirA/LeafA/BunchOfAs.txt' " +
                   "does not match fingerprint in database and is not newer. " +
                   "File could be damaged!",
                   "File 'test_tree/rootA/TreeA/DirA/LeafA/BunchOfBs.txt' " +
                   "does not match fingerprint in database and is not newer. " +
                   "File could be damaged!",
                   "File 'test_tree/rootA/LeafB/BunchOfAs.txt' does not match" +
                   " fingerprint in database and is not newer. File could be " +
                   "damaged!",
                   "File 'test_tree/rootA/LeafB/BunchOfBs.txt' does not match" +
                   " fingerprint in database and is not newer. File could be " +
                   "damaged!"]

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        exp_data = self.get_schema_5( mod_time, mod_time, target_name )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Populate filesystem with schema 1 with same modification time.
        tmp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( tmp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           target_name],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = list()
        for line in scr_out.split('\n'):
            warn_heading = 'WARNING] '
            idx = line.find(warn_heading)
            if 0 <= idx:
                scr_lines.append( line[ idx + len(warn_heading): ] )
            elif 0 < len(line):
                scr_lines.append( line )

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
        results = self.diff_trees( exp_data['roots'][target_name], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_existing_subtree(self):
        """Tests scan subcommand with an existing, changed subtree.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)

        # Populate the database with schema 5, modified 1 month ago.
        root_name = os.path.join('test_tree', 'rootA')
        exp_data = self.get_schema_5( mod_time, mod_time, root_name ) 
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        post_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( post_data )

        # Replce rootA/TreeA in expected data with changed subtree
        exp_data['roots'][root_name]['children']['TreeA'] = \
            post_data['roots']['rootA']['children']['TreeA']

        # Check targets
        target_name = os.path.join('test_tree', 'rootA', 'TreeA')
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           target_name],
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
        results = self.diff_trees( exp_data['roots'][root_name], 
                                   got_data['roots'][root_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_existing_file(self):
        """Tests scan subcommand with an existing, changed file.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)

        # Populate the database with schema 5, modified 1 month ago.
        root_name = os.path.join('test_tree', 'rootA')
        exp_data = self.get_schema_5( mod_time, mod_time, root_name ) 
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        post_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( post_data )

        # Replace rootA/LeafB/BunchOfAs.txt in expected data with changed record
        exp_data['roots'][root_name]['children']['LeafB']['children']\
            ['BunchOfAs.txt'] = post_data['roots']['rootA']['children']\
            ['LeafB']['children']['BunchOfAs.txt']

        # Check targets
        target_name = os.path.join('test_tree', 'rootA', 'LeafB', 
                                   'BunchOfAs.txt')
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           target_name],
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
        results = self.diff_trees( exp_data['roots'][root_name], 
                                   got_data['roots'][root_name] )

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
        rootA_name = os.path.join('test_tree', 'rootA')
        exp_data = { 'roots': dict(), 'Name': '' }
        tmp_schema = self.get_schema_1( mod_time, check_time )
        self.build_tree( tmp_schema )
        exp_data['roots'][rootA_name] = tmp_schema['roots']['rootA']

        # Build another schema 1 with a different root and add to expect data
        tmp_schema = self.get_schema_1( mod_time, check_time, 
                                        root_name = 'rootB', first_file_id=6,
                                        first_dir_id=6)
        self.build_tree( tmp_schema )
        rootB_name = os.path.join('test_tree', 'rootB')
        exp_data['roots'][rootB_name] = tmp_schema['roots']['rootB']

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           rootA_name, rootB_name],
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
        exp_data['roots'][rootA_name]['Name'] = rootA_name
        exp_data['roots'][rootB_name]['Name'] = rootB_name
        results = self.diff_trees( exp_data['roots'], 
                                   got_data['roots'] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )

    def test_root_prefix(self):
        """Tests scan subcommand with --root-prefix option.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time

        # Build tree with schema 1
        schema_data = self.get_schema_1( mod_time, check_time )
        self.build_tree( schema_data )

        # Update root name
        root_name = os.path.join('myTestPrefix', 'test_tree', 'rootA')
        exp_data = { 'Name': '', 
                     'roots': { root_name: schema_data['roots']['rootA'] } }
        exp_data['roots'][root_name]['Name'] = root_name

        # Populate the database with schema 1.
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check targets
        target_name = os.path.join('test_tree', 'rootA')
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           '--root-prefix', 'myTestPrefix',
                                           target_name],
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
        results = self.diff_trees( exp_data['roots'][root_name], 
                                   got_data['roots'][root_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_use_root(self):
        """Tests scan subcommand with --use-root option.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time

        # Build tree with schema 1
        schema_data = self.get_schema_1( mod_time, check_time )
        self.build_tree( schema_data )

        # Update root name
        root_name = os.path.join('myTestPrefix', 'rootA')
        exp_data = { 'Name': '', 
                     'roots': { root_name: schema_data['roots']['rootA'] } }
        exp_data['roots'][root_name]['Name'] = root_name

        # Populate the database with schema 1.
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check targets
        target_name = os.path.join('test_tree', 'rootA')
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           '--use-root', 'myTestPrefix',
                                           target_name],
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
        results = self.diff_trees( exp_data['roots'][root_name], 
                                   got_data['roots'][root_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_check_only_option(self):
        """Tests scan subcommand with --check-only option and alias --dry-run.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)
        exp_out = ["File 'test_tree/rootA/BunchOfCs.txt' is newer than " +
                   "database record. Marking as \"bad\"...",
                   "Subdirectory 'LeafB' no longer exists in directory " +
                   "'test_tree/rootA'!",
                   "File 'BunchOfAs.txt' no longer exists in directory " +
                   "'test_tree/rootA/LeafB'!",
                   "File 'BunchOfBs.txt' no longer exists in directory " +
                   "'test_tree/rootA/LeafB'!",
                   "File 'test_tree/rootA/TreeA/DirA/LeafA/BunchOfAs.txt' " +
                   'is newer than database record. Marking as "bad"...',
                   "File 'test_tree/rootA/TreeA/DirA/LeafA/BunchOfBs.txt' is " +
                   'newer than database record. Marking as "bad"...']

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        exp_data = self.get_schema_5( mod_time, mod_time, target_name )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Populate filesystem with a partial schema 1, modified recently
        tmp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        del(tmp_data['roots']['rootA']['children']['LeafB'])
        self.build_tree( tmp_data )

        # Check targets with --check-only
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           '--check-only', target_name],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = list()
        for line in scr_out.split('\n'):
            warn_heading = 'WARNING] '
            idx = line.find(warn_heading)
            if 0 <= idx:
                scr_lines.append( line[ idx + len(warn_heading): ] )
            elif 0 < len(line):
                scr_lines.append( line )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Get contents of database
        got_data = self.build_tree_data_from_db( self.conn.cursor() )
        self.conn.close()

        # Remove contents, LastChecked, and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID",
                                                "LastChecked"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID",
                                                "LastChecked"])
        results = self.diff_trees( exp_data['roots'][target_name], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
        # Check targets with --dry-run
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           '--dry-run', target_name],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = list()
        for line in scr_out.split('\n'):
            warn_heading = 'WARNING] '
            idx = line.find(warn_heading)
            if 0 <= idx:
                scr_lines.append( line[ idx + len(warn_heading): ] )
            elif 0 < len(line):
                scr_lines.append( line )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Get contents of database
        got_data = self.build_tree_data_from_db( self.conn.cursor() )
        self.conn.close()

        # Remove contents, LastChecked, and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID",
                                                "LastChecked"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID",
                                                "LastChecked"])
        results = self.diff_trees( exp_data['roots'][target_name], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def prune_helper_missing(self, option):
        """Tests scan subcommand with the specified alias for prune option and
        missing subdirectories.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)
        exp_out = list()

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        tmp_data = self.get_schema_5( mod_time, mod_time, target_name )
        self.populate_db_from_tree( tmp_data )
        self.conn.close()

        # Populate filesystem with a partial schema 1, modified recently
        exp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        del(exp_data['roots']['rootA']['children']['LeafB'])
        self.build_tree( exp_data )

        # Check targets with --prune
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           option, target_name],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
        scr_lines = list()
        for line in scr_out.split('\n'):
            warn_heading = 'WARNING] '
            idx = line.find(warn_heading)
            if 0 <= idx:
                scr_lines.append( line[ idx + len(warn_heading): ] )
            elif 0 < len(line):
                scr_lines.append( line )

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Get contents of database
        got_data = self.build_tree_data_from_db( self.conn.cursor() )
        self.conn.close()

        # Remove contents, LastChecked, and ID fields and compare
        exp_data = self.strip_fields(exp_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID",
                                                "LastChecked"])
        got_data = self.strip_fields(got_data, ["contents","File_ID",
                                                "Parent_ID","Path_ID",
                                                "LastChecked"])
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    def test_prune_long_missing(self):
        """Uses prune_helper_missing to test scan with the --prune option.
        """
        self.prune_helper_missing("--prune")
        
    def test_prune_short_missing(self):
        """Uses prune_helper_missing to test scan with the -p option.
        """
        self.prune_helper_missing("-p")
        
    def prune_helper_updated(self, option):
        """Tests scan subcommand with the specified alias for prune option and
        updated but not missing subdirectories.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        self.populate_db_from_tree( self.get_schema_5( mod_time, mod_time, 
                                                       target_name ) )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        exp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( exp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan', option,
                                           target_name],
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
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_prune_long_updated(self):
        """Uses prune_helper_updated to test scan with the --prune option.
        """
        self.prune_helper_updated("--prune")
        
    def test_prune_short_updated(self):
        """Uses prune_helper_updated to test scan with the -p option.
        """
        self.prune_helper_updated("-p")
        
    def helper_skip_recent_with_recent(self, option):
        """Tests scan subcommand with specified alias for --skip-recent option
        and a tree that has been checked within default window.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=29)

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        exp_data = self.get_schema_5( mod_time, mod_time, target_name )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        tmp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( tmp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           option, target_name],
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
        results = self.diff_trees( exp_data['roots'][target_name], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def helper_skip_recent_with_old(self, option):
        """Tests scan subcommand with specified alias for --skip-recent option
        and a tree that has been checked exactly default window days ago.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=30)

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        self.populate_db_from_tree( self.get_schema_5( mod_time, mod_time, 
                                                       target_name ) )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        exp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( exp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           option, target_name],
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
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )
        
    def test_skip_recent_long_with_recent(self):
        """Tests long version of --skip-recent with recently scanned path.
        """
        self.helper_skip_recent_with_recent("--skip-recent")
        
    def test_skip_recent_short_with_recent(self):
        """Tests short version of --skip-recent with recently scanned path.
        """
        self.helper_skip_recent_with_recent("-s")
        
    def test_skip_recent_long_with_old(self):
        """Tests long version of --skip-recent with path last scanned outside of
        window.
        """
        self.helper_skip_recent_with_old("--skip-recent")
        
    def test_skip_recent_short_with_old(self):
        """Tests short version of --skip-recent with path last scanned outside 
        of window.
        """
        self.helper_skip_recent_with_old("-s")
        
    def test_expr_option(self):
        """Tests scan subcommand with --skip-recent option, --expr set to
        something other than default, and a tree that has been checked exactly
        default window days ago.
        """

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        num_days = 29

        mod_time = datetime.datetime.fromtimestamp(int(float(time.time())))
        check_time = mod_time
        mod_time = mod_time - datetime.timedelta(days=num_days)

        # Populate the database with schema 5, modified 1 month ago.
        target_name = os.path.join('test_tree', 'rootA')
        self.populate_db_from_tree( self.get_schema_5( mod_time, mod_time, 
                                                       target_name ) )
        self.conn.close()

        # Populate filesystem with schema 1, modified recently
        exp_data = self.get_schema_1( check_time, check_time, 'rootA' )
        self.build_tree( exp_data )

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'scan',
                                           '--skip-recent', '--expr', 
                                           str(num_days), target_name],
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
        got_data['roots'][target_name]['Name'] = 'rootA'
        results = self.diff_trees( exp_data['roots']['rootA'], 
                                   got_data['roots'][target_name] )

        # Verify results 
        self.assertEqual( results['left'], None )
        self.assertEqual( results['right'], None )
        self.assertNotEqual( len(results['common']), 0 )

# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
