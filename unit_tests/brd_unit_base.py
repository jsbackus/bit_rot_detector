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
    os.link(script_name , 'brd.py' )

import brd

class BrdUnitBase(unittest.TestCase):
    """Base class for all brd-related unit tests. Provides various support
    functions but does not perform any tests.
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

    def read_in_chunks(self, file_obj, chunk_size=1024*1024):
        """Generator to read data from the specified file in chunks.
        Default chunk size is 1M.
        """
        while True:
            data = file_obj.read(chunk_size)
            if not data:
                break
            yield data

    def calc_fingerprint(self, filename, file_size=0):
        """Returns a string containing the SHA1 fingerprint of this file.
        """
        # Create a new SHA1 object and read from the specified file in chunks.
        result = hashlib.sha1()
    
        # Read file data
        with open(filename, 'rb') as f:
            for read_data in read_in_chunks(f):
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
            colStr = '(' + ('?,' * (len(cols) -1)) + '?) '
            dataStr = 'VALUES(' + ('?,' * (len(data) -1)) + '?)'
            cursor.execute("INSERT INTO '" + table_name  + "' " + colStr +
                           dataStr, cols + data)


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

    def build_dir(self, dir_dict, parent=''):
        """Builds a directory structure based on the specified dictionary. Keys
        that have dictionaries for values become directories. Keys that have 
        strings for values become files with the string as contents. 
        Note: Recursive!
        """

        for entry in dir_dict.keys():
            path = parent + dir_dict[ entry ]
            if type( dir_dict[ entry ] ) == 'dict':
                # Make the directory
                os.mkdir( path )

                # Process its children
                self.build_dir( dir_dict[ entry ], path )
            elif type( dir_dict[ entry ] ) == 'str':
                # Open file and dump contents to it
                with open(path, 'wt') as f:
                    f.write( dir_dict[ entry ] + os.linesep )
                
    def del_dir(self, path):
        """Calls shutil.rmtree to remove the specified directory tree.
        """
        shutil.rmtree(path)
