from __future__ import unicode_literals
import sqlite3
import hashlib
import os
import stat
import shutil
import unittest
import sys

# Build path to brd script
script_name = os.path.join( os.path.dirname( os.path.dirname( 
            os.path.abspath(__file__) ) ), 'brd')

# Import brd in order to use some of its functions
# Note: We need to create a symbolic link to "rename" 'brd' to 'brd.py' so
# that import will find it.
if not os.path.exists('brd.py'):
    os.symlink(script_name , 'brd.py' )

import brd

class BrdUnitBase(unittest.TestCase):
    """Base class for all brd-related unit tests. Provides various support
    functions but does not perform any tests.

    Many functions use a 'table data' data structure that contains information
    on directories and files. Each key represents a file or directory and each
    key's value is a dictionary that conforms to the following:
    * Directories:
      - 'Name' : record's name
      - 'children' : Dict of Children
      - 'Path_ID' : record's path ID
      - 'Parent_ID' : record's parent ID
      - 'LastChecked' : record's LastChecked value
    * Files:
      - 'Name' : record's name
      - 'contents' : A string containing the files contents.
      - 'File_ID' : record's file ID
      - 'Parent_ID' : record's parent ID
      - 'LastModified' : record's LastModified value
      - 'Fingerprint' : record's fingerprint
      - 'Size' : record's file size
    The exception to the above is the top-level, which is a dict that conforms
    to the following:
    * 'roots': A dict of directories that are root directories.
    * 'Name': The name of the top-level directory
    """

    def setUp(self):
        """Initialize data structures
        """

        # Define table names
        self.table_names = brd.table_names
        
        # Store script name/location for subclasses
        self.script_name = script_name
        
        # Define default database name
        self.default_db = os.path.basename(self.script_name) + '.db'

        # Remove the database, if it exists
        if os.path.exists( self.default_db ):
            os.unlink( self.default_db )

    def tearDown(self):
        """General cleanup
        """
        # Remove the database, if it exists
        if os.path.exists( self.default_db ):
            os.unlink( self.default_db )
        
    def read_in_chunks(self, file_obj, chunk_size=1024*1024):
        """Generator to read data from the specified file in chunks.
        Default chunk size is 1M.
        """
        while True:
            data = file_obj.read(chunk_size)
            if not data:
                break
            yield data

    def calc_fingerprint(self, filename):
        """Returns a string containing the SHA1 fingerprint of this file.
        """
        # Create a new SHA1 object and read from the specified file in chunks.
        result = hashlib.sha1()
    
        # Read file data
        with open(filename, 'rb') as f:
            for read_data in self.read_in_chunks(f):
                result.update(read_data)

        # Return fingerprint
        return result.hexdigest()

    def open_db(self, db_url, bOpenOnly):
        """Function to open the specified SQLite database and store the 
        Connection object in self.conn. If bOpenOnly is true, only opens the
        database. Otherwise uses brd.open_db().
        """

        if bOpenOnly:
            self.conn = sqlite3.connect(database=db_url, 
                                        detect_types=sqlite3.PARSE_DECLTYPES)
        else:
            self.conn = brd.open_db( db_url )

    def populate_db_table(self, table_name, table_data):
       """Populates the specified table of the currently open SQLite database
        with the data in the list of dictionaries. Expects the keys of each
        dictionary to match the columns of the table.
        """

       # Get a cursor object
       cursor = self.conn.cursor()

       for row in table_data:
           # Build lists of column names and column data
           cols = ()
           data = ()
           for entry in row.keys():
               cols += ( entry, )
               data += ( row[ entry ], )
               
           # Execute SQL statement
           colStr = '(' + ','.join(cols) + ')'
           dataStr = ' VALUES(' + ('?,' * (len(data) -1)) + '?)'
           cursor.execute("INSERT INTO '" + table_name  + "' " + colStr +
                          dataStr, data)
       self.conn.commit()

    def populate_db_from_tree(self, tree_data):
        """Uses populate_db_table() to populate the database with the values
        for the specified tree.
        """
        
        dir_table_info = []
        file_table_info = []

        # Maintain a queue of entries so that we can keep track of children.
        # Then go through each child, adding its info and any of its children
        # to the queue
        item_queue = [ ]
        for entry in tree_data['roots'].keys():
            item_queue.append( tree_data['roots'][ entry ] )

        while 0 < len(item_queue):
            item = item_queue.pop()
            
            if 'Path_ID' in item:
                # directory. Add children to queue, remove children entry
                # and add item to dir table.
                for child in item['children'].keys():
                    item_queue.append( item[ 'children' ][ child ] )
                del( item['children'] )
                dir_table_info.append( item )
            else:
                # file. Remove the contents column and then add to file table.
                del( item['contents'] )
                file_table_info.append( item )

        # Populate dirs table
        self.populate_db_table( self.table_names['dirs'], dir_table_info )
        # Populate files table
        self.populate_db_table( self.table_names['files'], file_table_info )

    def build_tree_data_from_db(self, cursor):
        """Builds a tree datastructure from the file and directory tables
        in a database via the specified cursor.
        """
        # TO DO
        pass

    def diff_tree_datas(self, left_tree, right_tree):
        """Compares the two tree data structures a-la diff. Returns three tree
        datastructures:
        * 'left' = All entries only in left_tree.
        * 'right' = All entries only in right_tree.
        * 'common' = All entries that are common.

        Note: directories can appear in both "only" trees if one or more of its
        children appear only in left_tree and one or more of its children
        appear only in the right_tree.
        """
        # TO DO
        pass

    def find_table(self, table_name):
        """Checks to see if the database contains a table with the specified 
        name.
        """

        # Get a cursor object
        cursor = self.conn.cursor()

        # Grab the list of tables and see if the directory table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cursor.fetchall():
            if (table[0] == table_name):
                # Found it.
                return True

        # Didn't find it
        return False

    def build_tree(self, tree_data, parent=''):
        """Builds a directory structure based on the specified table data
        data structure.
        Note: Recursive!
        """

        if len( parent ) <= 0:
            # Top level. Create a directory with the name in 'name' then
            # recursively process roots.
            if os.path.exists( tree_data['Name'] ):
                self.del_tree( tree_data['Name'] )

            os.mkdir( tree_data['Name'] )
            for subtree in tree_data['roots'].keys():
                self.build_tree( tree_data['roots'][subtree], 
                                 tree_data['Name'] )
        else:
            path = os.path.join( parent, tree_data['Name'] )
            # tree_data is a subtree or file. See which, then handle accordingly
            if 'Path_ID' in tree_data:
                # Directory. Create it and recursively process children
                os.mkdir( path )

                for subtree in tree_data['children'].keys():
                    self.build_tree( tree_data['children'][subtree], path )
            else:
                # File. Open it and dump contents to it
                with open(path, 'wt') as f:
                    f.write( tree_data['contents'] + os.linesep )
                
    def del_tree(self, path):
        """Calls shutil.rmtree to remove the specified directory tree.
        """
        shutil.rmtree(path)

    def get_schema_1(self, last_modified=None, last_checked=None):
        """Builds and returns a table_data object for general test.
        """
        table_data = { 'roots': dict(), 'Name': 'test_tree' }

        tmp_dir = { 'Path_ID': 5, 'Parent_ID': 4, 'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafA' }
        tmp_file = { 'contents': 'a'*256, 'File_ID': 2, 'Parent_ID': 5,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_file = { 'contents': 'b'*256, 'File_ID': 3, 'Parent_ID': 5,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_dir = { 'Path_ID': 4, 'Parent_ID': 3, 'LastChecked': last_checked,
                    'Name': 'DirA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': 3, 'Parent_ID': 1, 'LastChecked': last_checked,
                    'Name': 'TreeA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': 1, 'Parent_ID': -1, 'LastChecked': last_checked,
                    'Name': 'rootA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        table_data['roots'][ tmp_dir['Name'] ] = tmp_dir

        tmp_dir = { 'Path_ID': 2, 'Parent_ID': 1, 'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafB' }

        tmp_file = { 'contents': 'a'*256, 'File_ID': 4, 'Parent_ID': 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file


        tmp_file = { 'contents': 'b'*256, 'File_ID':5, 'Parent_ID': 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file
        
        table_data['roots']['rootA']['children'][ tmp_dir['Name'] ] = tmp_dir

        tmp_file = { 'contents': 'c'*256, 'File_ID':1, 'Parent_ID': 1,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'ff3785f53b503b7adb7e7a3b9eeef255eac0e276', 
                     'Name': 'BunchOfCs.txt' }

        table_data['roots']['rootA']['children'][ tmp_file['Name'] ] = tmp_file

        return table_data
    
