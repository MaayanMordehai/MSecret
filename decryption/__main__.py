
import argparse
import base64
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


def decrypt_file_name(name, password):

    ''' name - the file (or directory) encrypted name.
    password - the password we got to decrypt the name.

    decrypting the name.

    returning the decrypted name.'''

    e_name = base64.b32decode(name)
    len_iv = int(e_name[:2], 16)
    c = crypte.MyCipher(
        password,
        False,
        e_name[2:len_iv + 2]
    )
    return c.doFinal(e_name[len_iv + 2:])


def split_path(path):
    ''' path - full path of a file or directory

    spliting the file or directory name from the path

    return a tuple of the path (inclode \) and the name'''

    index = path.rfind('\\')
    if index == -1:
        return '', path
    return path[:index + 1], path[index + 1:]


def decrypt_dirs_files(
    file_or_dir_name,
    password,
    dir=None,
):
    ''' file_or_dir_name - the full path of the directory,
    or file inside the directory.
    password - the password to decrypt the directory.
    dir - the directory that the decryption of the file,
    or the directory, need to be in.

    decrypt a directory or a file.
    Recursion (for the case of directories inside of the directory).'''

    if os.path.isdir(file_or_dir_name):
        if not dir:
            to_dir = find_file_name_without_ending(file_or_dir_name)
        else:
            path, dir_name = split_path(file_or_dir_name)
            to_dir = dir + '\\' + decrypt_file_name(dir_name, password)
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)
        for file in os.listdir(file_or_dir_name):
            decrypt_dirs_files(
                file_or_dir_name + '\\' + file,
                password,
                to_dir,
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
                    decrypt_file_name(
                        name,
                        password,
                    ),
                ),
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                0o0666,
            )
        else:
            fd2 = os.open(
                find_file_name_without_ending(file_or_dir_name),
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                0o0666,
            )
        try:
            decrypt_file(fd, fd2, password)
        finally:
            os.close(fd)
            os.close(fd2)


def decrypt_file(fd, fd2, password):
    c = crypte.MyCipher(
        password,
        False,
        read_block(fd, int(read_block(fd, 2), 16)),
    )
    while True:
        block = read_block(fd, BLOCK_SIZE)
        if not block:
            break
        my_write(fd2, c.update(block))
    my_write(fd2, c.doFinal())


def main():
    file_or_dir_name, password, delete = frame.Show_Frame(False)
    file_or_dir_name = file_or_dir_name.encode('utf8')
    decrypt_dirs_files(
        file_or_dir_name,
        password,
    )

if __name__ == '__main__':
    main()
