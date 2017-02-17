
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

    ''' fd - the file descriptor of the file we want to read
    block_size - the number of bytes we want to read

    reading from file a block

    returning the text - what we read from file'''

    text = ''
    tmp = ''
    while True:
        tmp = os.read(fd, block_size)
        text += tmp
        if len(text) == block_size or not tmp:
            break
    return text


def my_write(fd, data):

    ''' fd - the file descriptor of the file we want to write to
    data - what we want to write to the file

    writing to the file the data'''

    while data:
        data = data[os.write(fd, data):]


def write_all_file(
    len_file,
    fd,
    what_to_write,
    block_size=BLOCK_SIZE
):

    ''' len_file - the lenght of the data that is written in the file.
    fd - the file descriptor of the file we want to write to.
    what_to_write - one character that we want to write over all the file.
    block_size - the size of a block
    (to make sure it works if there is a big file).

    writing to all of the file one character, block by block.'''

    os.lseek(fd, 0, 0)
    tmp = tmp2 = len_file
    while tmp > 0:
        if tmp2 > BLOCK_SIZE:
            tmp2 = BLOCK_SIZE
        my_write(fd, what_to_write*tmp2)
        tmp2 = tmp = tmp - tmp2


def get_str_len_iv(cipher):

    ''' returning the lenght of the iv as a string insted of a number'''

    if cipher.iv_lenght < 16:
        return '0' + str(hex(cipher.iv_lenght))[2]
    else:
        return str(hex(cipher.iv_lenght))[2:4]


def encrypt_file(fd, fd2, password):

    ''' fd - the file descriptor of the file we want to encrypt
    fd2 -  the file descriptor of the encrypted file
    password - the password we got to encrypt the file

    encrypt the file, and writing:
    2 bytes of lenght of iv, iv, encryption
    to the file of fd2

    returning the lenght of the data in the file'''

    len_file = 0
    c = crypte.MyCipher(password, True)
    my_write(fd2, get_str_len_iv(c) + c.iv)
    while True:
        block = read_block(fd, BLOCK_SIZE)
        len_file += len(block)
        if not block:
            break
        my_write(fd2, c.update(block))
    my_write(fd2, c.doFinal())
    return len_file


def encrypt_file_name(name, password):

    ''' name - the file (or directory) name.
    password - the password we got to encrypt the name.

    encrypting the name.

    returning the encrypted name.'''

    c = crypte.MyCipher(password, True)
    return base64.b32encode(
        get_str_len_iv(
            c,
        ) + c.iv + c.doFinal(
            name,
        ),
    )


def before_delete(
    len_file,
    fd,
    bitstruct,
    first_write,
    second_write
):
    ''' len_file - the lenght of the data that is written in the file.
    fd - the file descriptor of the file we want to write to,
    before deleting it.
    bitstruct - the Struct('B') value
    first_write - first byte we write to all file
    second_write - second byte we write to all file

    writing to all file 16 times:
    first byte, second byte and random byte'''

    for i in range(16):
        st = ''
        rand = random.randint(0, 255)
        write_all_file(len_file, fd, first_write)  # need to ask alon if inside
        write_all_file(len_file, fd, second_write)  # or not
        write_all_file(len_file, fd, bitstruct.pack(rand))


def split_path(path):
    ''' path - full path of a file or directory

    spliting the file or directory name from the path

    return a tuple of the path (inclode \) and the name'''

    index = path.rfind('\\')
    if index == -1:
        return '', path
    return path[:index + 1], path[index + 1:]


def encrypt_dirs_files(
    delete,
    file_or_dir_name,
    password,
    binstruct,
    first_write,
    second_write,
    dir=None,
):
    ''' delete - to delete the directory or not?
    file_or_dir_name - the full path of the directory,
    or file inside the directory.
    password - the password to encrypt the directory.
    binstruct, first_write, second_write - are for the delete.
    dir - the directory that the encryption of the file,
    or the directory, need to be in.

    encrypt a directory or a file.
    Recursion (for the case of directories inside of the directory).'''

    if os.path.isdir(file_or_dir_name):
        if not dir:
            to_dir = file_or_dir_name + ENCRYPTED_END
        else:
            path, dir_name = split_path(file_or_dir_name)
            to_dir = dir + '\\' + encrypt_file_name(dir_name, password)
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
        if delete:
            os.rmdir(file_or_dir_name)
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
        if dir:
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
        else:
            fd2 = os.open(
                file_or_dir_name + ENCRYPTED_END,
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                0o0666,
            )
        try:
            len_file = encrypt_file(fd, fd2, password)
            if delete:
                before_delete(
                    len_file,
                    fd,
                    binstruct,
                    first_write,
                    second_write,
                )
        finally:
            os.close(fd)
            os.close(fd2)
            if delete:
                os.remove(file_or_dir_name)


def main():
    file_or_dir_name, password, delete = frame.Show_Frame(True)
    file_or_dir_name = file_or_dir_name.encode('utf8')
    bitstruct = struct.Struct('B')
    first_write = bitstruct.pack(0)
    second_write = bitstruct.pack(0xff)
    encrypt_dirs_files(
        delete,
        file_or_dir_name,
        password,
        bitstruct,
        first_write,
        second_write,
    )


if __name__ == '__main__':
    main()
