
import argparse
import base64
import os
import random
import struct


from ..common import crypte
from ..common import frame


ENCRYPTED_END = '.encrypted'
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

def write_all_file(len_file, fd, what_to_write, block_size=BLOCK_SIZE):
    os.lseek(fd, 0, 0)
    tmp = tmp2 = len_file
    while tmp > 0:
        if tmp2 > BLOCK_SIZE:
            tmp2 = BLOCK_SIZE
        my_write(fd, what_to_write*tmp2)
        tmp2 = tmp = tmp - tmp2

def get_str_iv(cipher):
    if cipher.iv_lenght < 16:
        return '0' + str(hex(cipher.iv_lenght))[2]
    else:
        return str(hex(cipher.iv_lenght))[2:4]

def encrypt_file(fd, fd2, password):
    len_file = 0
    c = crypte.MyCipher(password, True)
    my_write(fd2, get_str_iv(c) + c.iv)
    while True:
        block = read_block(fd, BLOCK_SIZE)
        len_file += len(block)
        if not block:
            break
        my_write(fd2, c.update(block))
    my_write(fd2, c.doFinal())
    return len_file

def encrypt_file_name(file_name, password):
    c = crypte.MyCipher(password, True)
    k = c.doFinal(file_name)
    to_file = get_str_iv(c) + c.iv + k
    return base64.b32encode(to_file)

def before_delete(
    len_file,
    fd,
    bitstruct,
    first_write,
    second_write
):
    for i in range(16):
        st = ''
        rand = random.randint(0,255)
        write_all_file(len_file, fd, first_write)
        write_all_file(len_file, fd, second_write)
        write_all_file(len_file, fd, bitstruct.pack(rand))

def split_path(path):
    index = path.rfind('\\')
    if index == -1:
        return '' , path
    return path[:index + 1], path[index + 1:]

'''
encrypt a directory. Recursion (for the case of directories inside of the directory).
dir = the directory that the encryption of a file or a directory given need to be in
binstruct, first_write, second_write - are for the delete.
'''
def encrypt_dirs_files(
    delete,
    file_or_dir_name,
    password,
    binstruct,
    first_write,
    second_write,
    dir=None,
):
    if os.path.isdir(file_or_dir_name):
        if dir == None:
            to_dir = file_or_dir_name + ENCRYPTED_END
        else:
            path, dir_name = split_path(file_or_dir_name)
            to_dir = dir +'\\'+ encrypt_file_name(dir_name, password)
        path, name = split_path(file_or_dir_name)
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)
        for file in os.listdir(file_or_dir_name):
            encrypt_dirs_files(
                delete,
                file_or_dir_name + '\\' + file,
                password,
                binstruct,
                first_write,
                second_write,
                to_dir,
            )
    else:
        if delete:
            fd = os.open(
                file_or_dir_name,
                os.O_RDWR,
            0o0666,
        )
        else:
            fd = os.open(
                file_or_dir_name,
                os.O_RDONLY,
                0o0666,
            )
        path, name = split_path(file_or_dir_name)
        fd2 = os.open(
            '%s\%s' % (
                dir,
                encrypt_file_name(
                    name,
                    password,
                ),
            ),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o0666,
        )
        try:
            len_file = encrypt_file(fd, fd2, password)
            if delete:
                before_delete(len_file, fd, binstruct, first_write, second_write)
        finally:
            os.close(fd)
            os.close(fd2)
            if delete:
                os.remove(file)


def main():
    file_or_dir_name, password, delete = frame.Show_Frame(True)
    file_or_dir_name = file_or_dir_name.encode('utf8')
    bitstruct = struct.Struct('B')
    first_write = bitstruct.pack(0)
    second_write = bitstruct.pack(0xff)
    if os.path.isdir(file_or_dir_name):
        encrypt_dirs_files(
            delete,
            file_or_dir_name,
            password,
            bitstruct,
            first_write,
            second_write,
        )
    else:
        if delete:
            fd = os.open(
                file_or_dir_name,
                os.O_RDWR,
                0o0666,
            )
        else:
            fd = os.open(
                file_or_dir_name,
                os.O_RDONLY,
                0o0666,
            )
        to_file = file_or_dir_name + ENCRYPTED_END
        fd2 = os.open(
            to_file,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o0666,
        )
        try:
            len_file = encrypt_file(file_or_dir_name, to_file, password)
            if delete:
                before_delete(len_file, fd, binstruct, first_write, second_write)
        finally:
            os.close(fd)
            os.close(fd2)
            if delete:
                os.remove(file_or_dir_name)


if __name__ == '__main__':
    main()
