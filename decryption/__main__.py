
import argparse
import os
import struct


from ..common import crypte
from ..common import frame


BLOCK_SIZE = 1024


def find_file_name_without_ending(name):
    index = name.rfind('.')
    if index == -1:
        return name
    return name[:index]


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


def open_files(file_name):
    fd = os.open(
        file_name,
        os.O_RDONLY,
        0o0666,
    )
    to_file = find_file_name_without_ending(file_name)
    fd2 = os.open(
        to_file,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        0o0666,
    )
    return fd, fd2


def main():
    file_name, password, delete = frame.Show_Frame(False)
    fd, fd2 = open_files(file_name)
    try:
        c = crypte.MyCipher(
            password,
            False,
            read_block(
                fd,
                int(
                    read_block(
                        fd,
                        2,
                    ), 16,
                ),
            ),
        )
        while True:
            block = read_block(fd, BLOCK_SIZE)
            if not block:
                break
            my_write(fd2, c.update(block))
        my_write(fd2, c.doFinal())

    finally:
        os.close(fd)
        os.close(fd2)

if __name__ == '__main__':
    main()
