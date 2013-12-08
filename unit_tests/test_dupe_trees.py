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

class TestDupeTrees(BrdUnitBase):
    """Unit tests for the dupe_trees subcommand.
    """

    def setUp(self):
        # Call superclass's setup routine.
        super(TestDupeTrees,self).setUp()
        
    def tearDown(self):
        # Call superclass's cleanup routine
        super(TestDupeTrees,self).tearDown()

    def test_identical_trees(self):
        """Tests dupe_trees subcommand with identical trees.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        exp_out = \
            ['2 dirs with Fingerprint ' +
             '0x4c02e31639d05130158e820ea66dd9b87bd385b1:',
             '    [rootB]', '    [rootA]', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        exp_data = self.get_schema_2( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_dissimilar_trees(self):
        """Tests dupe_trees subcommand with dissimilar trees.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        exp_out = ['']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( 
            self.get_schema_1( str(mod_time), check_time ) )
        # Populate the database with schema 3.
        self.populate_db_from_tree( 
            self.get_schema_3( str(mod_time), check_time ) )
        self.conn.close()

        # Check targets
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )
        
    def test_output_option(self):
        """Tests dupe_trees subcommand with --output option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        out_file = 'test_output.txt'
        exp_out = \
            ['2 dirs with Fingerprint ' +
             '0x4c02e31639d05130158e820ea66dd9b87bd385b1:\n',
             '    [rootB]\n', '    [rootA]\n']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 2.
        exp_data = self.get_schema_2( str(mod_time), check_time )
        self.populate_db_from_tree( exp_data )
        self.conn.close()

        # Check --output
        scr_out = subprocess.check_output([self.script_name,  'dupe_trees', 
                                           '--output', out_file], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        with open(out_file, 'rt') as f:
            scr_lines = f.readlines()

        # Verify results
        self.assertEqual( scr_out, '' )

        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

        # Remove output file and try again with -o option
        os.unlink( out_file )

        # Check -o
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees', 
                                           '-o', out_file], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        with open(out_file, 'rt') as f:
            scr_lines = f.readlines()

        # Verify results
        self.assertEqual( scr_out, '' )

        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

        # Clean up
        os.unlink( out_file )
        
    def test_nofilefp_option(self):
        """Tests dupe_trees subcommand with --nofilefp option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        check_out = ['']
        exp_out = ['2 dirs with Fingerprint ' + 
                   '0x9ba569116eee959eae815d7c3d1f2bf81e518526:',
                   '    [rootA]/TreeA/DirA', '    [rootD]/TreeD/DirA', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( 
            self.get_schema_1( str(mod_time), check_time ) )
        # Populate the database with schema 3.
        self.populate_db_from_tree( 
            self.get_schema_3( str(mod_time), check_time ) )
        self.conn.close()

        # Check targets normally.
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(check_out) )
        for exp_line in check_out:
            self.assertTrue( exp_line in scr_lines )

        # Check targets with --nofilefp
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees',
                                           '--nofilefp'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    def test_nofilename_option(self):
        """Tests dupe_trees subcommand with --nofilename option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        check_out = ['']
        exp_out = ['2 dirs with Fingerprint ' + 
                   '0x24c3d1d9c9c6c8303b19cc1a2def771a6e787b4d:',
                   '    [rootA]', '    [rootB]', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 4
        self.populate_db_from_tree( 
            self.get_schema_4( str(mod_time), check_time ) )
        self.conn.close()

        # Check targets normally.
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(check_out) )
        for exp_line in check_out:
            self.assertTrue( exp_line in scr_lines )

        # Check targets with --nofilename
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees',
                                           '--nofilename'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    def test_nosubdirfp_option(self):
        """Tests dupe_trees subcommand with --nosubdirfp option
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        check_out = ['']
        exp_out = ['2 dirs with Fingerprint ' +
                     '0xa937d97faf45931eeb5690804c2d26d519c06cf9:', 
                     '    [rootA]/TreeA/DirA', 
                     '    [rootD]/TreeD/DirA', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 1.
        self.populate_db_from_tree( 
            self.get_schema_1( str(mod_time), check_time ) )
        # Populate the database with schema 3.
        self.populate_db_from_tree( 
            self.get_schema_3( str(mod_time), check_time ) )
        self.conn.close()

        # Check targets normally.
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(check_out) )
        for exp_line in check_out:
            self.assertTrue( exp_line in scr_lines )

        # Check targets with --nofilename
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees',
                                           '--nosubdirfp'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    def test_nodirname_option(self):
        """Tests dupe_trees subcommand with --nodirname option.
        """

        mod_time = int(time.time())
        check_time = datetime.datetime.fromtimestamp(mod_time)
        check_out = ['2 dirs with Fingerprint '+
                     '0x4c02e31639d05130158e820ea66dd9b87bd385b1:',
                     '    [rootB]', '    [rootA]', '']

        exp_out = ['2 dirs with Fingerprint ' +
                   '0x85f1d8f066c57b7650d1733f40b23fa7597df836:', 
                   '    [rootB]', '    [rootA]', 
                   '4 dirs with Fingerprint ' +
                   '0x183831bb75375e5a0fdd885c3b4425472519b7e9:', 
                   '    [rootA]/LeafB', '    [rootB]/TreeA/DirA/LeafA', 
                   '    [rootA]/TreeA/DirA/LeafA', 
                   '    [rootB]/LeafB', '']

        # Call open_db, which should create db and its tables
        self.open_db( self.default_db, False )

        # Populate the database with schema 2
        self.populate_db_from_tree( 
            self.get_schema_2( str(mod_time), check_time ) )
        self.conn.close()

        # Check targets normally.
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results
        self.assertEqual( len(scr_lines), len(check_out) )
        for exp_line in check_out:
            self.assertTrue( exp_line in scr_lines )

        # Check targets with --nodirname
        scr_out = subprocess.check_output([self.script_name, 'dupe_trees',
                                           '--nodirname'], 
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)

        scr_lines = scr_out.split('\n')

        # Verify results 
        self.assertEqual( len(scr_lines), len(exp_out) )
        for exp_line in exp_out:
            self.assertTrue( exp_line in scr_lines )

    # def test_single_tree_with_duplicates(self):
    #     """Tests dupe_trees subcommand with a single tree that has duplicate
    #     files.
    #     """

    #     mod_time = int(time.time())
    #     check_time = datetime.datetime.fromtimestamp(mod_time)
    #     exp_out = \
    #         ['2 files with Fingerprint ' +
    #          '0x1a0372738bb5b4b8360b47c4504a27e6f4811493:',
    #          '    [rootA]/TreeA/DirA/LeafA/BunchOfAs.txt',
    #          '    [rootA]/LeafB/BunchOfAs.txt',
    #          '2 files with Fingerprint ' +
    #          '0xfa75bf047f45891daee8f1fa4cd2bf58876770a5:',
    #          '    [rootA]/TreeA/DirA/LeafA/BunchOfBs.txt',
    #          '    [rootA]/LeafB/BunchOfBs.txt', '']

    #     # Call open_db, which should create db and its tables
    #     self.open_db( self.default_db, False )

    #     # Populate the database with schema 1.
    #     exp_data = self.get_schema_1( str(mod_time), check_time )
    #     self.populate_db_from_tree( exp_data )
    #     self.conn.close()

    #     # Check targets
    #     scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
    #                                       stderr=subprocess.STDOUT,
    #                                       universal_newlines=True)

    #     scr_lines = scr_out.split('\n')

    #     # Verify results 
    #     self.assertEqual( len(scr_lines), len(exp_out) )
    #     for exp_line in exp_out:
    #         self.assertTrue( exp_line in scr_lines )
        
    # def test_single_tree_without_duplicates(self):
    #     """Tests dupe_trees subcommand with a single tree that does not have 
    #     duplicate files.
    #     """

    #     mod_time = int(time.time())
    #     check_time = datetime.datetime.fromtimestamp(mod_time)
    #     exp_out = ''

    #     # Call open_db, which should create db and its tables
    #     self.open_db( self.default_db, False )

    #     # Populate the database with schema 1.
    #     exp_data = self.get_schema_3( str(mod_time), check_time )
    #     self.populate_db_from_tree( exp_data )
    #     self.conn.close()

    #     # Check targets
    #     scr_out = subprocess.check_output([self.script_name, 'dupe_trees'], 
    #                                       stderr=subprocess.STDOUT,
    #                                       universal_newlines=True)

    #     # Verify results 
    #     self.assertEqual( scr_out, exp_out )
        
# Allow unit test to run on its own
if __name__ == '__main__':
    unittest.main()
