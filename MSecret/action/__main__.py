#
## @package MSecret.__main__
## @file __main__.py Implementation of @ref MSecret.__main__
#


import argparse
import os
import wx


from ..common import code_file
from ..common import frame
from ..common import delete
from ..common import save


## ENCRYPTED_END of encryptions
ENCRYPTED_END = '.MSecret'
## BLOCK_SIZE for read and write to\from file
BLOCK_SIZE = 1024
## optional ENCRYPTIONS
ENCRYPTIONS = ['AES', 'MSecret']


## geting arguments
# @param commands (dictinary) the commands possible : the function
#
def parse_args(commands):
    """Parse program arguments."""

    yes_no = {'yes': True, 'no': False}
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--command',
        required=True,
        type=str,
        choices=sorted(commands.keys()),
        help='encrypt or decrypt or delete the source file/dir',
    )
    parser.add_argument(
        '--src-file',
        required=True,
        nargs='+',
        type=str,
        help='source file to encrypt or decrypt or delete (command)',
    )
    parser.add_argument(
        '--dst-file',
        default=None,
        nargs='+',
        type=str,
        help="destination file to write there the encryption or decryption.",
    )
    parser.add_argument(
        '--delete',
        default=sorted(yes_no.keys())[0],
        type=str,
        choices=sorted(yes_no.keys()),
        help='if you want to delete the source file write yes.',
    )
    parser.add_argument(
        '--recursive',
        default=sorted(yes_no.keys())[0],
        type=str,
        choices=sorted(yes_no.keys()),
        help='yes if you want to do the command to dirs inside dirs?',
    )
    parser.add_argument(
        '--encryption',
        default=ENCRYPTIONS[0],
        type=str,
        choices=ENCRYPTIONS,
        help='which encryption???',
    )
    parser.add_argument(
        '--passphrase',
        default=None,
        type=str,
        help='%s%s' % (
            'secret passphrase, ',
            'if not specified will be acquired by user interface',
        ),
    )

    args = parser.parse_args()
    args.delete = yes_no[args.delete]
    args.recursive = yes_no[args.recursive]
    args.src_file =  ' '.join(args.src_file)
    if args.dst_file is not None:
        args.dst_file =  ' '.join(args.dst_file)
    return args


## encrypt the file
# @param password (str) password
# @param src (str) source file name
# @param dst (str) destination file name
# @param delete (bool) delete the file\s?
# @param password (bool) recursive(if dir)?
# @param enc (str) the encryption
#
def encrypt(password, src, dst, delete, recur, enc):
    if password is None:
        password, enc, recur, exit = frame.Show_Frame(src, True)
    if not exit:
        if dst is None:
            dst = '%s%s' % (src, ENCRYPTED_END)
        encrypt_dir_or_file(
            password,
            src,
            dst,
            recur,
            delete,
            enc,
        )


## decrypt the file
# @param password (str) password
# @param src (str) source file name
# @param dst (str) destination file name
# @param delete (bool) delete the file\s?
# @param password (bool) recursive(if dir)?
# @param enc (str) the encryption
#
def decrypt(password, src, dst, delete, recur):
    if password is None:
        password, enc, recur, exit = frame.Show_Frame(src, False)
    if not exit:
        if dst is None:
            dst = without_encrypted_ending(src)
        decrypt_dir_or_file(
            password,
            src,
            dst,
            recur,
            delete,
        )


## write file data into code_file
# @param codefile (CodeFile object)
# @param first_file (str) source file name
#
def encrypt_file(first_file, codefile):
    with open(first_file, 'rb') as fh:
        with code_file.MyOpen(codefile, 'w') as cf:
            while True:
                tmp = fh.read(BLOCK_SIZE)
                if not tmp:
                    break
                cf.write(tmp)


## encrypt a file\directory
# @param password (str) password
# @param src (str) source file name
# @param dst (str) destination file name
# @param delete (bool) delete the file\s?
# @param password (bool) recursive(if dir)?
# @param enc (str) the encryption
#
def encrypt_dir_or_file(password, src, dst, recursive, delet, enc):
    if os.path.isdir(src):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for file in os.listdir(src):
            if os.path.isdir(os.path.join(src, file)):
                if recursive:
                    encrypt_dir_or_file(
                        password,
                        os.path.join(src, file),
                        os.path.join(
                            dst,
                            '%s%s' % (file, ENCRYPTED_END),
                        ),
                        recursive,
                        delet,
                        enc,
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
                        enc,
                    ),
                )
                if delet:
                    delete.delete_file_properly(os.path.join(src, file))
        if delet and recursive:
            os.rmdir(src)
    else:
        encrypt_file(src, code_file.CodeFile(dst, password, enc))
        if delet:
            delete.delete_file_properly(src)


## read code_file data to file
# @param codefile (CodeFile object)
# @param file_name (str) source file name
#
def decrypt_file(codefile, file_name):
    with code_file.MyOpen(codefile, 'r') as cf:
        with open(file_name, 'wb') as fh:
            while True:
                text = cf.read(BLOCK_SIZE)
                if not text:
                    break
                fh.write(text)


## decrypt a file\directory
# @param password (str) password
# @param src (str) source file name
# @param dst (str) destination file name
# @param delete (bool) delete the file\s?
# @param password (bool) recursive(if dir)?
#
def decrypt_dir_or_file(password, src, dst, recursive, delet):
    if os.path.isdir(src):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for file in os.listdir(src):
            if os.path.isdir(os.path.join(src, file)):
                if recursive:
                    decrypt_dir_or_file(
                        password,
                        os.path.join(src, file),
                        os.path.join(
                            dst,
                            without_encrypted_ending(file),
                        ),
                        recursive,
                        delet,
                    )
            else:
                decrypt_file(
                    code_file.CodeFile(os.path.join(src, file), password),
                    os.path.join(
                        dst,
                        without_encrypted_ending(file),
                    ),
                )
                if delet:
                    delete.delete_file_properly(os.path.join(src, file))
        if delet and recursive:
            os.rmdir(src)
    else:
        decrypt_file(code_file.CodeFile(src, password), dst)
        if delet:
            delete.delete_file_properly(src)


## remove encrypt end
# @param name (str) file name
#
def without_encrypted_ending(name):
    if name[-len(ENCRYPTED_END):] == ENCRYPTED_END:
        return name[:-len(ENCRYPTED_END)]
    return name


## directory special mode
# @param dir (str) dir name
#
def directory_mode(dir):
    password, enc, recu, exit = frame.Show_Frame(dir, True, False)
    if not exit:
        s = save.Save()
        s.password = password
        s.encryption = enc
        s.dir_name = dir
        app2 = wx.App(False)
        frame2 = frame.FilesAndOptions(None, s)
        frame2.Show()
        app2.MainLoop()


## Main implementation.
def main():
    commands = {
        'encrypt': encrypt,
        'decrypt': decrypt,
        'delete': delete.delete_file_properly,
        'directory': directory_mode,
    }
    args = parse_args(commands)
    if args.command == 'delete':
        commands[args.command](args.src_file)
    elif args.command == 'decrypt':
        commands[args.command](
            args.passphrase,
            args.src_file,
            args.dst_file,
            args.delete,
            args.recursive,
        )
    elif args.command == 'encrypt':
        commands[args.command](
            args.passphrase,
            args.src_file,
            args.dst_file,
            args.delete,
            args.recursive,
            args.encryption,
        )
    else:
        commands[args.command](
            args.src_file
        )


if __name__ == '__main__':
    main()
