
import argparse
import base64
import os
import random
import struct


from ..common import code_file
from ..common import crypte
from ..common import frame


YES_NO = ['yes', 'no']
ENCRYPTED_END = '.encrypted'
BLOCK_SIZE = 1024
BITSTRUCT = struct.Struct('B')
FIRST_WRITE = BITSTRUCT.pack(0)
SECOND_WRITE = BITSTRUCT.pack(0xff)


def parse_args(COMMANDS):
    """Parse program arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--command',
        required=True,
        type=str,
        choices=sorted(COMMANDS.keys()),
        help='encrypt or decrypt or delete the source file/dir',
    )
    parser.add_argument(
        '--src-file',
        required=True,
        type=str,
        help='source file to encrypt or decrypt or delete (command). required.',
    )
    parser.add_argument(
        '--dst-file',
        default=None,
        type=str,
        help="destination file to write there the encryption or decryption. default - source file.encrypted",
    )
    parser.add_argument(
        '--delete',
        default=YES_NO[1],
        type=str,
        choices=YES_NO,
        help='if you want to delete the source file write yes, else no, default - no.',
    )
    parser.add_argument(
        '--recursive',
        default=YES_NO[1],
        type=str,
        choices=YES_NO,
        help='Do you want to do the command to diractories inside diractories?, if yes write "yes" - perform operation recursive, else write no, default - "no"',
    )
    parser.add_argument(
        '--passphrase',
        default=None,
        type=str,
        help='a secret passphrase, if not specified will be acquired by user interface',
    )

    args = parser.parse_args()
    return args


def delete(args):
    delete_file_or_dir_properly(args.src_file, args.recursive)


def encrypt(args):
    if args.passphrase is None:
        password = frame.Show_Frame(args.src_file)
    else:
        password = args.passphrase
    if args.dst_file is not None:
        dst = args.dst_file
    else:
        dst = '%s%s' % (args.src_file, ENCRYPTED_END)
    encrypt_dir_or_file(password, args.src_file, dst, args.recursive, args.delete)


def decrypt(args):
    if args.passphrase is None:
        password = frame.Show_Frame(args.src_file)
    else:
        password = args.passphrase
    if args.dst_file is not None:
        dst = args.dst_file
    else:
        dst = without_encrypted_ending(args.src_file)
    decrypt_dir_or_file(password, args.src_file, dst, args.recursive, args.delete)


def encrypt_file(first_file, codefile):
    with open(first_file, 'rb') as fh:
        with code_file.MyOpen(codefile, 'w') as cf:
            while True:
                tmp = fh.read(BLOCK_SIZE)
                if not tmp:
                    break
                cf.write(tmp)


def encrypt_dir_or_file(password, src, dst, recursive, delete):
    if os.path.isdir(src):
        if not os.path.exists(dst):
            os.mkdir(dst)
        for file in os.listdir(src):
            if os.path.isdir(os.path.join(src, file)):
                if recursive == YES_NO[0]:
                    encrypt_dir_or_file(
                        password,
                        os.path.join(src, file),
                        os.path.join(
                            dst,
                            '%s%s' % (file, ENCRYPTED_END),
                        ),
                        recursive,
                        delete,
                    )

            else:
                encrypt_file(
                    os.path.join(src, file),
                    code_file.CodeFile(
                        os.path.join(
                            dst,
                            '%s%s' % (file, ENCRYPTED_END),
                        ),
                        password,
                    ),
                )
                if delete == YES_NO[0]:
                    delete_file_properly(os.path.join(src, file))
        if delete == YES_NO[0]:
            os.rmdir(src)
    else:
        encrypt_file(src, code_file.CodeFile(dst, password))
        if delete == YES_NO[0]:
            delete_file_properly(src)


def decrypt_file(codefile, file_name):
    with code_file.MyOpen(codefile, 'r') as cf:
        with open(file_name, 'w') as fh:
            while True:
                text = cf.read(BLOCK_SIZE)
                if not text:
                    break
                fh.write(text)


def decrypt_dir_or_file(password, src, dst, recursive, delete):
    if os.path.isdir(src):
        if not os.path.exists(dst):
            os.mkdir(dst)
        for file in os.listdir(src):
            if os.path.isdir(os.path.join(src, file)):
                if recursive == YES_NO[0]:
                    decrypt_dir_or_file(
                        password,
                        os.path.join(src, file),
                        os.path.join(
                            dst,
                            without_encrypted_ending(file),
                        ),
                        recursive,
                        delete,
                    )
            else:
                decrypt_file(
                    code_file.CodeFile(os.path.join(src, file), password),
                    os.path.join(
                        dst,
                        without_encrypted_ending(file),
                    ),
                )
                if delete == YES_NO[0]:
                    delete_file_properly(os.path.join(src, file))
        if delete == YES_NO[0]:
            os.rmdir(src)
    else:
        decrypt_file(code_file.CodeFile(src, password), dst)
        if delete == DELETE[0]:
            delete_file_properly(src)



def without_encrypted_ending(name):
    if name[-10:] == ENCRYPTED_END:
        return name[:-10]
    return name


def delete_file_or_dir_properly(file, recursive):
    if os.path.isdir(file):
        for f in os.listdir(file):
            if os.path.isdir(file):
                if recursive:
                    delete_file_or_dir_properly(
                        os.path.join(file, f),
                        recursive,
                    )
            else:
                delete_file_properly(os.path.join(file, f))
        os.rmdir(file)
    else:
        delete_file_properly(file)


def write_all_file(len_file, fh, what_to_write, block_size=BLOCK_SIZE):

    ''' len_file - the length of the data that is written in the file.
    what_to_write - one character that we want to write over all the file.
    block_size - the size of a block
    (to make sure it works if there is a big file).

    writing to all of the file one character, block by block.'''

    fh.seek(0, 0)
    tmp = tmp2 = len_file
    while tmp > 0:
        if tmp2 > BLOCK_SIZE:
            tmp2 = BLOCK_SIZE
        fh.write(what_to_write*tmp2)
        tmp2 = tmp = tmp - tmp2


def delete_file_properly(file, len_file=None):
    ''' len_file - the length of the data that is written in the file.
    file - the name of the file we want to encrypt

    writing to all file 16 times:
    first byte - 0, second byte - 0xff and random byte'''
    len_file = os.path.getsize(file)
    with open(file, 'w') as fh:
        for i in range(16):
            st = ''
            rand = random.randint(0, 255)
            write_all_file(len_file, fh, FIRST_WRITE)
            write_all_file(len_file, fh, SECOND_WRITE)
            write_all_file(len_file, fh, BITSTRUCT.pack(rand))
    os.remove(file)


def main():
    COMMANDS = {'encrypt': encrypt, 'decrypt': decrypt, 'delete': delete}
    args = parse_args(COMMANDS)
    COMMANDS[args.command](args)


if __name__ == '__main__':
    main()