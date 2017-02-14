
import argparse
import os
import random
import struct


from ..common import crypte
from ..common import frame


FILE_ENCRYPTED_END = '.encrypted'
BLOCK_SIZE = 1024


def read_block(fd, block_size):
    text = ''
    tmp = ''
    while True:
        tmp = os.read(fd, block_size)
        text += tmp
        if len(text) == block_size or not tmp:
            break
    return text


def my_write(fd, data):
    while data:
        data = data[os.write(fd, data):]


def open_files(file_name, delete):
    if delete:
        fd = os.open(
            file_name,
            os.O_RDWR,
            0o0666,
        )
    else:
        fd = os.open(
            file_name,
            os.O_RDONLY,
            0o0666,
        )
    to_file = file_name + FILE_ENCRYPTED_END
    fd2 = os.open(
        to_file,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        0o0666,
    )
    return fd, fd2

def write_all_file(len_file, fd, what_to_write, block_size=BLOCK_SIZE):
    os.lseek(fd, 0, 0)
    tmp = tmp2 = len_file
    while tmp > 0:
        if tmp2 > BLOCK_SIZE:
            tmp2 = BLOCK_SIZE
        my_write(fd, what_to_write*tmp2)
        tmp2 = tmp = tmp - tmp2

def handel_iv(cipher, fd2):
    if cipher.iv_lenght < 16:
        iv_len_in_str = '0' + str(hex(cipher.iv_lenght))[2]
    else:
        iv_len_in_str = str(hex(cipher.iv_lenght))[2:4]
    my_write(fd2, iv_len_in_str + cipher.iv)


def main():
    file_name, password, delete = frame.Show_Frame(True)
    fd, fd2 = open_files(file_name, delete)
    if delete:
        len_file = 0
    try:
        c = crypte.MyCipher(password, True)
        handel_iv(c, fd2)
        while True:
            block = read_block(fd, BLOCK_SIZE)
            if delete:
                len_file += len(block)
            if not block:
                break
            my_write(fd2, c.update(block))
        my_write(fd2, c.doFinal())

        if delete:
            bitstruct = struct.Struct('B')
            for i in range(16):
                st = ''
                rand = random.randint(0,255)
                write_all_file(len_file, fd, bitstruct.pack(0))
                write_all_file(len_file, fd, bitstruct.pack(0xff))
                write_all_file(len_file, fd, bitstruct.pack(rand))

    finally:
        os.close(fd)
        os.close(fd2)
        if delete:
            os.remove(file_name)

if __name__ == '__main__':
    main()
