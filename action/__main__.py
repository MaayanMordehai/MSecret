
import argparse
import base64
import os
import random
import struct


from ..common import code_file
from ..common import crypte
from ..common import frame


COMMANDS = ['encrypt', 'decrypt', 'delete']
ENCRYPTED_END = '.encrypted'
BLOCK_SIZE = 1024
BITSTRUCT = struct.Struct('B')
FIRST_WRITE = BITSTRUCT.pack(0)
SECOND_WRITE = BITSTRUCT.pack(0xff)

def parse_args():
    """Parse program arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--command',
        required=True,
        type=str,
        help='%s or %s or %s the sorce file/dir' % (COMMANDS[0], COMMANDS[1], COMMANDS[2]),
    )
    parser.add_argument(
        '--src-file',
        required=True,
        type=str,
        help='sorce file to encrypt or decrypt or delete (command). required.',
    )
    parser.add_argument(
        '--dst-file',
        default=None,
        type=str,
        help="destination file to write there the encryption or decryption. defualt - sorce file.encrypted",
    )
    parser.add_argument(
        '--delete',
        default=False,
        type=bool,
        help='if you want to delete the sorce file write True, else False, defualt - False.',
    )
    parser.add_argument(
        '--recursive',
        default=False,
        type=bool,
        help='Do you want to do the command to diractories inside diractories?, if yes write "True" - perform operation recursive, else write False, default - "False"',
    )
    parser.add_argument(
        '--passphrase',
        default=None,
        type=str,
        help='a secret passphrase, if not specified will be acquired by user interface',
    )

    args = parser.parse_args()
    return args


def encrypt_file(first_file, codefile):
    try:
        fd = os.open(
            first_file,
            os.O_RDONLY,
            0o0666,
        )
        with code_file.MyOpen(codefile, 'w') as cf:
            text = ''
            tmp = ''
            while True:
                tmp = read_block(fd, BLOCK_SIZE)
                if not tmp:
                    break
                cf.write(tmp)
                tmp = ''
    finally:
        os.close(fd)

def my_write(fd, data):
    while data:
        data = data[os.write(fd, data):]


def decrypt_file(codefile, file_name):
    with code_file.MyOpen(codefile, 'r') as cf:
        try:
            fd = os.open(
                file_name,
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                0o0666,
            )
            text = ''
            while True:
                text = cf.read(BLOCK_SIZE)
                if not text:
                    break
                my_write(fd, text)
        finally:
            os.close(fd)


def encrypt_diractory(password, dir, encrypted_dir_name):
    dirs_in_dir = []
    if not os.path.exists(encrypted_dir_name):
        os.makedirs(encrypted_dir_name)
    for root, dirs, files in os.walk(dir):
        if root == dir:
            for name in files:
                codefile = code_file.CodeFile(
                    encrypted_dir_name +'\\'+ name + ENCRYPTED_END,
                    password,
                )
                print os.path.join(root, name)
                encrypt_file(os.path.join(root, name), codefile)
            for dir1 in dirs:
                dirs_in_dir.append(dir1)
    return dirs_in_dir


def without_encrypted_ending(name):
    if name[-10:] == ENCRYPTED_END:
        return name[:-10]
    return name


def decrypt_diractory(password, dir, decrypted_name):
    dirs_in_dir = []
    if not os.path.exists(decrypted_name):
        os.makedirs(decrypted_name)
    for root, dirs, files in os.walk(dir):
        if root == dir:
            for name in files:
                codefile = code_file.CodeFile(os.path.join(root, name), password)
                decrypt_file(
                    codefile,
                    decrypted_name + '\\' + without_encrypted_ending(name),
                )
            for dir1 in dirs:
                dirs_in_dir.append(dir1)
    return dirs_in_dir


def encrypt_diractory_recorsive(password, dir, encrypt_dir_name):
    dirs_in_dir = encrypt_diractory(password, dir, encrypt_dir_name)
    for dir1 in dirs_in_dir:
        new_dir = encrypt_dir_name + '\\' + dir1 + ENCRYPTED_END
        encrypt_diractory_recorsive(password, dir + '\\' + dir1, new_dir)


def decrypt_diractory_recorsive(password, dir, decrypt_dir_name):
    dirs_in_dir = decrypt_diractory(password, dir, decrypt_dir_name)
    for dir1 in dirs_in_dir:
        new_dir = decrypt_dir_name + '\\' + without_encrypted_ending(dir1)
        decrypt_diractory_recorsive(password, dir + '\\' + dir1, new_dir)

def read_block(fd, block_size):
        '''
        fd - the file descriptor of the file we want to read
        block_size - the number of bytes we want to read

        reading from file a block

        returning the text - what we read from file
        '''
        text = ''
        tmp = ''
        while True:
            tmp = os.read(fd, block_size)
            text += tmp
            if len(text) == block_size or not tmp:
                break
        return text


def write_all_file(len_file, fd, what_to_write, block_size=BLOCK_SIZE):

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


def delete_file_properly(file, len_file=None):
    ''' len_file - the lenght of the data that is written in the file.
    file - the name of the file we want to encrypt

    writing to all file 16 times:
    first byte - 0, second byte - 0xff and random byte'''

    if len_file is None:
        fd = os.open(
            file,
            os.O_RDWR,
            0o0666,
        )
        len_file = 0
        while True:
            block = read_block(fd, BLOCK_SIZE)
            if not block:
                break
            len_file += len(block)

    else:
        fd = os.open(
            file,
            os.O_WRONLY,
            0o0666,
        )

    try:
        for i in range(16):
            st = ''
            rand = random.randint(0, 255)
            write_all_file(len_file, fd, FIRST_WRITE)
            write_all_file(len_file, fd, SECOND_WRITE)
            write_all_file(len_file, fd, BITSTRUCT.pack(rand))
    finally:
        os.close(fd)
        os.remove(file)


def delete_all_files_in_dir_properly(dir):
    dirs_in_dir = []
    for root, dirs, files in os.walk(dir):
        if root == dir:
            for name in files:
                delete_file_properly(os.path.join(root, name))
            for dir1 in dirs:
                dirs_in_dir.append(dir1)
    return dirs_in_dir


def delete_all_files_in_dirs_recursive(dir):
    dirs_in_dir = delete_all_files_in_dir_properly(dir)
    for dir1 in dirs_in_dir:
        delete_all_files_in_dirs_recursive(dir + '\\' + dir1)
    os.rmdir(dir)


def main():
    args = parse_args()
    if args.passphrase is None and not args.command == COMMANDS[2]:
        password = frame.Show_Frame(args.src_file).encode('utf8')
    elif not args.command == COMMANDS[2]:
        password = args.passphrase

    if args.command == COMMANDS[0]:
        if args.dst_file is not None:
            dst = args.dst_file
        else:
            dst = args.src_file + ENCRYPTED_END

        if os.path.isdir(args.src_file):
            if args.recursive:
                encrypt_diractory_recorsive(password, args.src_file, dst)
            else:
                encrypt_diractory(password, args.src_file, dst)
        else:
            encrypt_file(args.src_file, code_file.CodeFile(dst, password))

    elif args.command == COMMANDS[1]:
        if args.dst_file is not None:
            dst = args.dst_file
        else:
            dst = without_encrypted_ending(args.src_file)

        if os.path.isdir(args.src_file):
            if args.recursive:
                decrypt_diractory_recorsive(password, args.src_file, dst)
            else:
                decrypt_diractory(password, args.src_file, dst)
        else:
            decrypt_file(code_file.CodeFile(args.src_file, password), dst)

    if args.command == COMMANDS[2] or args.delete:
        if os.path.isdir(args.src_file):
            if args.recursive:
                delete_all_files_in_dirs_recursive(args.src_file)
            else:
                delete_all_files_in_dir_properly(args.src_file)
        else:
            delete_file_properly(args.src_file)


if __name__ == '__main__':
    main()
