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
import sqlite3
import hashlib
import os
import stat
import shutil
import unittest
import sys
import datetime

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

        # Maintain a list of temporary files to remove and put
        # default database in list.
        self.tmp_files = [ self.default_db ]

        # Pre-clean files
        self.cleanTmpFiles()

    def tearDown(self):
        """General cleanup
        """
        # Remove temporary files
        self.cleanTmpFiles()

    def cleanTmpFiles(self):
        """Removes all temporary files currently in the list.
        """

#        for tmp_file in self.tmp_files:
#            if os.path.exists( tmp_file ):
#                os.unlink( tmp_file )

    def addTmpFile( self, file_name ):
        """Adds a temporary file to the list of temp files to remove.
        """
        self.tmp_files.append( file_name )
        
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
               if entry == "LastModified" and row[ entry ] != None:
                   row[ entry ] = row[ entry ].timestamp()
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

        # Make a deep copy of tree_data so that we don't damage it.
        lcl_data = self.strip_fields(tree_data, '')

        # Maintain a queue of entries so that we can keep track of children.
        # Then go through each child, adding its info and any of its children
        # to the queue
        item_queue = [ ]
        for entry in lcl_data['roots'].keys():
            item_queue.append( lcl_data['roots'][ entry ] )

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

    def build_tree_data_from_db(self, cursor, path_id = -1):
        """Builds a tree datastructure from the file and directory tables
        in a database via the specified cursor, starting with the specified
        path.
        
        Note: This function is recursive.
        """
        
        ret_val = dict()

        # If path_id is valid, grab information from directory table
        if 0 <= path_id:
            cursor.execute("SELECT Name,Parent_ID,LastChecked FROM '" + 
                           self.table_names['dirs'] + "' WHERE Path_ID=?", 
                           (path_id,))
            for row in cursor.fetchall():
                ret_val['Name'] = row[0]
                ret_val['Path_ID'] = path_id
                ret_val['Parent_ID'] = row[1]
                ret_val['LastChecked'] = row[2]
                ret_val['children'] = dict()
                child_dict = ret_val['children']
            
                # Look for children in the file table
                cursor.execute("SELECT File_ID,Name,LastModified,Fingerprint," +
                               "Size from '" + self.table_names['files'] + 
                               "' WHERE Parent_ID=?", (path_id,))
                for file_row in cursor.fetchall():
                    name = file_row[1]
                    child_dict[ name ] = dict()
                    child_dict[ name ]['Name'] = name
                    child_dict[ name ]['contents'] = ''
                    child_dict[ name ]['File_ID'] = file_row[0]
                    child_dict[ name ]['Parent_ID'] = path_id
                    child_dict[ name ]['LastModified'] = \
                        datetime.datetime.fromtimestamp( \
                        int(float(file_row[2])) )
                    child_dict[ name ]['Fingerprint'] = file_row[3]
                    child_dict[ name ]['Size'] = file_row[4]
        else:
            ret_val['Name'] = ''
            ret_val['roots'] = dict()
            child_dict = ret_val['roots']

        # Grab list of child directories from database and process
        cursor.execute("SELECT Name,Path_ID FROM '" + self.table_names['dirs']
                       + "' WHERE Parent_ID=?", (path_id,))
        for row in cursor.fetchall():
            name = row[0]
            child_dict[ name ] = self.build_tree_data_from_db( cursor, row[1] )

        return ret_val

    def strip_fields(self, tree, field_names):
        """Recursively deep-copies the specified dict-of-dicts, removing the
        specified field name(s) at each level from the copy to be returned.
        """

        ret_val = dict()

        # Allow user to specify a signel string
        if isinstance(field_names, list):
            lcl_fields = field_names
        else:
            lcl_fields = [ field_names ]

        for entry in tree:
            if not entry in lcl_fields:
                if isinstance(tree[ entry ], dict):
                    ret_val[ entry ] = self.strip_fields(tree[ entry ], 
                                                         lcl_fields)
                else:
                    ret_val[ entry ] = tree[ entry ]

        return ret_val

    def diff_trees(self, left_tree, right_tree):
        """Recursively performs a deep compare of two objects. Limited to
        the following data types:
        * dict
        * list
        * str
        * int
        * tuple
        * datetime.datetime

        Returns:
        * 'left' = All entries different in left_tree.
        * 'right' = All entries different in right_tree.
        * 'common' = All entries that are common.
        """
        
        ret_val = { 'left': None, 'right': None, 'common': None }
        header_list = ( 'left', 'right', 'common' )
        
        # Check simple use cases
        if left_tree == None and right_tree == None:
            return ret_val

        if left_tree == None:
            ret_val['right'] = right_tree
            return ret_val

        if right_tree == None:
            ret_val['left'] = left_tree
            return ret_val

        if left_tree == right_tree:
            ret_val['common'] = left_tree
            return ret_val

        # Check base types
        if type(left_tree) != type(right_tree) :
            ret_val['left'] = left_tree
            ret_val['right'] = right_tree
            return ret_val

        if isinstance(left_tree, str) or isinstance(left_tree, int):
            if left_tree == right_tree:
                ret_val['common'] = left_tree
            else:
                ret_val['left'] = left_tree
                ret_val['right'] = right_tree
            return ret_val

        if isinstance(left_tree, datetime.datetime):
            max_delta = datetime.timedelta(minutes=1)
            tmp_delta = abs(left_tree - right_tree)
            if tmp_delta < max_delta:
                ret_val['common'] = left_tree
            else:
                ret_val['left'] = left_tree
                ret_val['right'] = right_tree
            return ret_val

        if isinstance(left_tree, list):
            for header in header_list:
                ret_val[ header ] = []
            
            for idx in range(0, len(left_tree)):
                result = self.diff_trees( left_tree[idx], right_tree[idx] )
                for header in header_list:
                    if result[ header ] != None:
                        ret_val[ header ] += result[ header ]

            for header in header_list:
                if len(ret_val[ header ]) == 0:
                    ret_val[ header ] = None

            return ret_val

        if isinstance(left_tree, tuple):
            for header in header_list:
                ret_val[ header ] = []
            
            for idx in range(0, len(left_tree)):
                result = self.diff_trees( left_tree[idx], right_tree[idx] )
                for header in header_list:
                    if result[ header ] != None:
                        ret_val[ header ] += result[ header ]

            for header in header_list:
                if len(ret_val[ header ]) == 0:
                    ret_val[ header ] = None
                else:
                    ret_val[ header ] = tuple( ret_val[ header ] )
            
            return ret_val

        if isinstance(left_tree, dict):
            for header in header_list:
                ret_val[ header ] = dict()

            tmp_entry_list = dict()
            for entry in left_tree:
                tmp_entry_list[ entry ] = 1
            for entry in right_tree:
                tmp_entry_list[ entry ] = 1

            for entry in tmp_entry_list:
                if entry in left_tree:
                    tmp_left = left_tree[ entry ]
                else:
                    tmp_left = None

                if entry in right_tree:
                    tmp_right = right_tree[ entry ]
                else:
                    tmp_right = None

                result = self.diff_trees( tmp_left, tmp_right )

                for header in header_list:
                    if result[ header ] != None:
                        ret_val[ header ][ entry ] = result[ header ]
                
            for header in header_list:
                if len(ret_val[ header ]) == 0:
                    ret_val[ header ] = None

            return ret_val

        # Should never get to this point. Throw a TypeError if we do.
        raise TypeError('Type "' + str(type(left_tree)) + '" not supported!')

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
#            if os.path.exists( tree_data['Name'] ):
#                self.del_tree( tree_data['Name'] )

            if not os.path.exists( tree_data['Name'] ):
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

                # Update utime and atime.
                tmp_time = tree_data['LastModified'].timestamp()
                os.utime( path, ( tmp_time, tmp_time ) )
                
    def del_tree(self, path):
        """Calls shutil.rmtree to remove the specified directory tree.
        """
        shutil.rmtree(path)

    def get_schema_1(self, last_modified=None, last_checked=None, 
                     root_name='rootA', first_file_id=1, first_dir_id=1):
        """Builds and returns a table_data object for general test.
        """

        table_data = { 'roots': dict(), 'Name': 'test_tree' }

        tmp_dir = { 'Path_ID': first_dir_id + 4, 'Parent_ID': first_dir_id + 3, 
                    'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafA' }
        tmp_file = { 'contents': 'a'*256, 'File_ID': first_file_id + 4, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_file = { 'contents': 'b'*256, 'File_ID': first_file_id + 3,
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_dir = { 'Path_ID': first_dir_id + 3, 'Parent_ID': first_dir_id + 1,
                    'LastChecked': last_checked,
                    'Name': 'DirA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 1, 'Parent_ID': first_dir_id + 0,
                    'LastChecked': last_checked,
                    'Name': 'TreeA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_file_id + 0, 
                    'Parent_ID': -1, 'LastChecked': last_checked,
                    'Name': root_name, 'children': { tmp_dir['Name'] : tmp_dir }
                    }
        
        table_data['roots'][ tmp_dir['Name'] ] = tmp_dir

        tmp_dir = { 'Path_ID': first_dir_id + 2, 'Parent_ID': first_dir_id + 0, 
                    'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafB' }

        tmp_file = { 'contents': 'a'*256, 'File_ID': first_file_id + 2, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file


        tmp_file = { 'contents': 'b'*256, 'File_ID': first_file_id + 1, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file
        
        table_data['roots'][root_name]['children'][ tmp_dir['Name'] ] = tmp_dir

        tmp_file = { 'contents': 'c'*256, 'File_ID': first_file_id + 0, 
                     'Parent_ID': first_dir_id + 0,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'b145bb8710c9b6624bb46631eecc3bbcc335d0ab', 
                     'Name': 'BunchOfCs.txt' }

        table_data['roots'][root_name]['children'][ tmp_file['Name'] ] = tmp_file

        return table_data
    
    def get_schema_2(self, last_modified=None, last_checked=None, 
                     root_name='rootB', first_file_id=6, first_dir_id=6):
        """Builds and returns a table_data object for general test.
        """

        table_data = { 'roots': dict(), 'Name': 'test_tree' }

        # Create a schema similar to schema 1 but with different directory
        # names.
        tmp_dir = { 'Path_ID': first_dir_id + 4, 'Parent_ID': first_dir_id + 3, 
                    'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafD' }
        tmp_file = { 'contents': 'a'*256, 'File_ID': first_file_id + 4, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_file = { 'contents': 'b'*256, 'File_ID': first_file_id + 3, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_dir = { 'Path_ID': first_dir_id + 3, 'Parent_ID': first_dir_id + 1,
                    'LastChecked': last_checked,
                    'Name': 'DirD', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 1, 'Parent_ID': first_dir_id + 0,
                    'LastChecked': last_checked,
                    'Name': 'TreeD', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_file_id + 0, 
                    'Parent_ID': -1, 'LastChecked': last_checked,
                    'Name': root_name, 'children': { tmp_dir['Name'] : tmp_dir }
                    }
        
        table_data['roots'][ tmp_dir['Name'] ] = tmp_dir

        tmp_dir = { 'Path_ID': first_dir_id + 2, 'Parent_ID': first_dir_id + 0, 
                    'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafE' }

        tmp_file = { 'contents': 'a'*256, 'File_ID': first_file_id + 2, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file


        tmp_file = { 'contents': 'b'*256, 'File_ID': first_file_id + 1, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file
        
        table_data['roots'][root_name]['children'][ tmp_dir['Name'] ] = tmp_dir

        tmp_file = { 'contents': 'c'*256, 'File_ID': first_file_id + 0, 
                     'Parent_ID': first_dir_id + 0,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'b145bb8710c9b6624bb46631eecc3bbcc335d0ab', 
                     'Name': 'BunchOfCs.txt' }

        table_data['roots'][root_name]['children'][ tmp_file['Name'] ] = tmp_file

        return table_data
    
    def get_schema_3(self, last_modified=None, last_checked=None, 
                     root_name='rootD', first_file_id=16, first_dir_id=16):
        """Builds and returns a table_data object for general test.
        """
        table_data = { 'roots': dict(), 'Name': 'test_tree' }

        tmp_dir = { 'Path_ID': first_dir_id + 4, 
                    'Parent_ID': first_dir_id + 3, 'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafA' }
        tmp_file = { 'contents': 'f'*256, 'File_ID': first_file_id + 4, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'a5ff36b8df5d62c3284d70bfcb149fc519712d46',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_file = { 'contents': 'g'*256, 'File_ID': first_file_id + 3, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'ba5cba06c22bb5448d87118c2a68a7db2c0dd1bd', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_dir = { 'Path_ID': first_dir_id + 3, 
                    'Parent_ID': first_dir_id + 1, 'LastChecked': last_checked,
                    'Name': 'DirA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 1, 
                    'Parent_ID': first_dir_id + 0, 'LastChecked': last_checked,
                    'Name': 'TreeD', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 0, 'Parent_ID': -1, 
                    'LastChecked': last_checked,
                    'Name': root_name, 'children': { tmp_dir['Name'] : tmp_dir }
                    }
        
        table_data['roots'][ tmp_dir['Name'] ] = tmp_dir

        tmp_dir = { 'Path_ID': first_dir_id + 2, 
                    'Parent_ID': first_dir_id + 0, 'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafC' }

        tmp_file = { 'contents': 'd'*256, 'File_ID': first_file_id + 2, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '765101b7f5b353693477d6636011513e2be795df',
                     'Name': 'BunchOfDs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file


        tmp_file = { 'contents': 'e'*256, 'File_ID': first_file_id + 1, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'bd7b61341bfa37a21026883c90da697997f43745', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file
        
        table_data['roots'][root_name]['children'][ tmp_dir['Name'] ] = tmp_dir

        tmp_file = { 'contents': 'h'*256, 'File_ID': first_file_id + 0, 
                     'Parent_ID': first_dir_id + 0,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'a8ae4254b998ecafdc841ebf0fd13da3baab49f7', 
                     'Name': 'BunchOfCs.txt' }

        table_data['roots'][root_name]['children'][ tmp_file['Name'] ] = tmp_file

        return table_data
    
    def get_schema_4(self, last_modified=None, last_checked=None,
                     root_name='rootB', first_file_id=6, first_dir_id=6):

        """Builds and returns a table_data object for general test.
        """
        table_data = { 'roots': dict(), 'Name': 'test_tree' }

        # Create a root identical to schema 1 with different file names
        tmp_dir = { 'Path_ID': first_dir_id + 4, 'Parent_ID': first_dir_id + 3, 
                    'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafA' }
        tmp_file = { 'contents': 'a'*256, 'File_ID': first_file_id + 4, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfDs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_file = { 'contents': 'b'*256, 'File_ID': first_file_id + 3, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfEs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_dir = { 'Path_ID': first_dir_id + 3, 'Parent_ID': first_dir_id + 1,
                    'LastChecked': last_checked,
                    'Name': 'DirA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 1, 'Parent_ID': first_dir_id + 0,
                    'LastChecked': last_checked,
                    'Name': 'TreeA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_file_id + 0, 
                    'Parent_ID': -1, 'LastChecked': last_checked,
                    'Name': root_name, 'children': { tmp_dir['Name'] : tmp_dir }
                    }
        
        table_data['roots'][ tmp_dir['Name'] ] = tmp_dir

        tmp_dir = { 'Path_ID': first_dir_id + 2, 'Parent_ID': first_dir_id + 0, 
                    'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafB' }

        tmp_file = { 'contents': 'a'*256, 'File_ID': first_file_id + 2, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '1a0372738bb5b4b8360b47c4504a27e6f4811493',
                     'Name': 'BunchOfDs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file


        tmp_file = { 'contents': 'b'*256, 'File_ID': first_file_id + 1, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'fa75bf047f45891daee8f1fa4cd2bf58876770a5', 
                     'Name': 'BunchOfEs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file
        
        table_data['roots'][root_name]['children'][ tmp_dir['Name'] ] = tmp_dir

        tmp_file = { 'contents': 'c'*256, 'File_ID': first_file_id + 0, 
                     'Parent_ID': first_dir_id + 0,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'b145bb8710c9b6624bb46631eecc3bbcc335d0ab', 
                     'Name': 'BunchOfFs.txt' }

        table_data['roots'][root_name]['children'][ tmp_file['Name'] ] = tmp_file

        return table_data
    
    def get_schema_5(self, last_modified=None, last_checked=None, 
                     root_name='rootA', first_file_id=1, first_dir_id=1):
        """Builds and returns a table_data object for general test.
        """
        # Schema similar to schema 1 but with different file contents.
        table_data = { 'roots': dict(), 'Name': 'test_tree' }

        tmp_dir = { 'Path_ID': first_dir_id + 4, 
                    'Parent_ID': first_dir_id + 3, 'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafA' }
        tmp_file = { 'contents': 'f'*256, 'File_ID': first_file_id + 4, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'a5ff36b8df5d62c3284d70bfcb149fc519712d46',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_file = { 'contents': 'g'*256, 'File_ID': first_file_id + 3, 
                     'Parent_ID': first_dir_id + 4,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'ba5cba06c22bb5448d87118c2a68a7db2c0dd1bd', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file

        tmp_dir = { 'Path_ID': first_dir_id + 3, 
                    'Parent_ID': first_dir_id + 1, 'LastChecked': last_checked,
                    'Name': 'DirA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 1, 
                    'Parent_ID': first_dir_id + 0, 'LastChecked': last_checked,
                    'Name': 'TreeA', 'children': { tmp_dir['Name'] : tmp_dir } }
        
        tmp_dir = { 'Path_ID': first_dir_id + 0, 'Parent_ID': -1, 
                    'LastChecked': last_checked,
                    'Name': root_name, 'children': { tmp_dir['Name'] : tmp_dir }
                    }
        
        table_data['roots'][ tmp_dir['Name'] ] = tmp_dir

        tmp_dir = { 'Path_ID': first_dir_id + 2, 
                    'Parent_ID': first_dir_id + 0, 'LastChecked': last_checked,
                    'children': dict(), 'Name': 'LeafB' }

        tmp_file = { 'contents': 'd'*256, 'File_ID': first_file_id + 2, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': '765101b7f5b353693477d6636011513e2be795df',
                     'Name': 'BunchOfAs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file


        tmp_file = { 'contents': 'e'*256, 'File_ID': first_file_id + 1, 
                     'Parent_ID': first_dir_id + 2,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'bd7b61341bfa37a21026883c90da697997f43745', 
                     'Name': 'BunchOfBs.txt' }
        tmp_dir['children'][ tmp_file['Name'] ] = tmp_file
        
        table_data['roots'][root_name]['children'][ tmp_dir['Name'] ] = tmp_dir

        tmp_file = { 'contents': 'h'*256, 'File_ID': first_file_id + 0, 
                     'Parent_ID': first_dir_id + 0,
                     'LastModified': last_modified, 'Size': 257,
                     'Fingerprint': 'a8ae4254b998ecafdc841ebf0fd13da3baab49f7', 
                     'Name': 'BunchOfCs.txt' }

        table_data['roots'][root_name]['children'][ tmp_file['Name'] ] = tmp_file

        return table_data
    
