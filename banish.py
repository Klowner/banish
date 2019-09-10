#!/usr/bin/env python3

from pathlib import Path
import argparse
import hashlib
import os
import sqlite3
import sys


BLOCKSIZE = 1024000
DB_LOCATION = str(Path.home()) + '/.local/banish'

print(DB_LOCATION)
parser = argparse.ArgumentParser(description='Banish files')
parser.add_argument('filename')


def check_dirs():
    if not os.path.exists(DB_LOCATION):
        os.makedirs(DB_LOCATION)


def database_is_missing(db_path):
    return not os.path.exists(db_path)


def get_db():
    db_path = DB_LOCATION + '/banish.db'
    check_dirs()
    if database_is_missing(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE signatures (hash blob[40], size integer)''')
        conn.execute('''CREATE UNIQUE INDEX signatures_idx ON signatures (hash, size)''')
        return conn
    else:
        return sqlite3.connect(db_path)


def banish(filename):
    with open(filename, 'rb') as fd:
        (hash_digest, filesize) = checksum(fd)
        conn = get_db()
        conn.execute('INSERT OR REPLACE INTO signatures (hash, size) VALUES (?, ?)', [hash_digest, filesize])
        conn.commit()
        conn.close()
    return hash_digest.hex()


def checksum(fd):
    hasher = hashlib.sha1()
    size = 0
    fd.seek(0)
    buf = fd.read(BLOCKSIZE)
    while buf:
        hasher.update(buf)
        buf = fd.read(BLOCKSIZE)
        size += len(buf)
    return (hasher.digest(), fd.tell())


if __name__ == '__main__':
   args = parser.parse_args()
   if args.filename:
       print(banish(args.filename))
