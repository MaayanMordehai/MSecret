
import argparse
import os
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


def main():
    file_name, password, delete = frame.Show_Frame(True)
    fd, fd2 = open_files(file_name, delete)
    try:
        c = crypte.MyCipher(password, True)
        iv_len = c.get_iv_lenght()
        if iv_len < 16:
            iv_len_in_str = '0' + str(hex(iv_len))[2]
        else:
            iv_len_in_str = str(hex(iv_len))[2:4]
        my_write(fd2, iv_len_in_str + c.get_iv())
        current_posi = 0
        while True:
            block = read_block(fd, BLOCK_SIZE)
            if not block:
                break
            my_write(fd2, c.update(block))
            if delete:
                end_posi = os.lseek(fd, 0, os.SEEK_CUR)
                os.lseek(fd, current_posi, 0)
                w = ''
                while len(block) > len(w):
                    w += struct.pack(
                        'B',
                        0,
                    ) + struct.pack(
                        'B',
                        0xff,
                    ) + os.urandom(6)
                if len(w) > len(block):
                    w = w[:len(block) - len(w)]
                my_write(fd, w)
                current_posi = os.lseek(fd, 0, os.SEEK_CUR)
        my_write(fd2, c.doFinal())

    finally:
        os.close(fd)
        os.close(fd2)
        if delete:
            os.remove(file_name)

if __name__ == '__main__':
    main()
