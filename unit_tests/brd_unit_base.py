from __future__ import unicode_literals
import sqlite3
import hashlib
import os
import stat

class BrdUnitBase(unittest.TestCase):
    """Base class for all brd-related unit tests. Provides various support
    functions but does not perform any tests.
    """

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

def open_db(self, db_url):
    """Function to open the specified SQLite database and store the Connection
    object in self.conn.
    """

    # Connect to database
    self.conn = sqlite3.connect(database=db_url, 
                                detect_types=sqlite3.PARSE_DECLTYPES)

    
