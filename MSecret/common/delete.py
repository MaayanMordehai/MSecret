#
## @package MSecret.delete delete file safe moudle.
## @file delete.py Implementation of @ref MSecret.delete
#


import os
import random
import struct


## block_size of write to file
BLOCK_SIZE = 1024
## turning str to binary with BITSTRUCT
BITSTRUCT = struct.Struct('B')
## first write to all file
FIRST_WRITE = BITSTRUCT.pack(0)
## second write to all file
SECOND_WRITE = BITSTRUCT.pack(0xff)


## delete file safely
# @param file (str) file name to delete
# @param block_size (int) block_size of write to file
#
def delete_file_properly(file, block_size=BLOCK_SIZE):
    ''' len_file - the length of the data that is written in the file.
    file - the name of the file we want to encrypt

    writing to all file 16 times:
    first byte - 0, second byte - 0xff and random byte'''
    len_file = os.path.getsize(file)
    with open(file, 'r+') as fh:
        write_all_file(
            fh,
            FIRST_WRITE,
            len_file,
            block_size,
        )
        write_all_file(
            fh,
            SECOND_WRITE,
            len_file,
            block_size,
        )
        for i in range(6):
            write_all_file(
                fh,
                BITSTRUCT.pack(
                    random.randint(
                        0,
                        255,
                    )
                ),
                len_file,
                block_size,
            )

    os.remove(file)


## write to all file
# @param fh (file handeling object) file handeling
# @param what_to_write (int) what to write to all file
# @param left_to_write (int) how much left to write
# @param block_size (int) block size of write to file
#
def write_all_file(fh, what_to_write, left_to_write, block_size=BLOCK_SIZE):
    fh.seek(0, 0)
    while left_to_write > 0:
        fh.write(what_to_write * block_size)
        left_to_write -= block_size