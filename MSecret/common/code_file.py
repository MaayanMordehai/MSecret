#
## @package MSecret.code_file encrypted files module.
## @file code_file.py Implementation of @ref MSecret.code_file
#


import crypte


## my encryption name
MY_ENCRYPTION = "MSecret"
## AES encryption name
AES = "AES"


## Encrypted file object
#
# handelling encrypted files
#
class CodeFile(object):

    ## Constructor
    def __init__(self, file_name, password, enc=None):
        self._file_name = file_name
        self._fh = None
        self._password = password
        self._iv_read = None
        self._read_cip = None
        self._write_cip = None
        self._did_final_read = False
        self._encryption = enc

    ## open encrypted file
    # @param read_or_write (string) open to read or write
    #
    def open(self, read_or_write):
        if read_or_write == 'r':
            self._fh = open(self._file_name, 'rb')
            self._encryption = self._fh.read(int(self._fh.read(2), 16))
            self._iv_read = self._fh.read(int(self._fh.read(2), 16))
            if self._encryption == MY_ENCRYPTION:
                self._read_cip = crypte.MyCipher(
                    self._password,
                    False,
                    self._iv_read,
                )
            elif self._encryption == AES:
                self._read_cip = crypte.AesCipher(
                    self._password,
                    False,
                    self._iv_read,
                )
            else:
                raise ValueError("we don't support this encryption")
        elif read_or_write == 'w':
            self._fh = open(self._file_name, 'wb')
            len_en = len(self._encryption)
            if len_en < 16:
                len_en_str = '0%s' % str(hex(len_en))[2]
            else:
                len_en_str = str(hex(len_en))[2:4]
            if self._encryption == MY_ENCRYPTION:
                self._write_cip = crypte.MyCipher(
                    self._password,
                    True,
                )
            elif self._encryption == AES:
                self._write_cip = crypte.AesCipher(
                    self._password,
                    True,
                )
            else:
                raise ValueError(
                    "this program doesn't support this encryption"
                )
            self._fh.write(
                '%s%s' % (
                    len_en_str,
                    self._encryption,
                )
            )
            if self._write_cip.iv_lenght < 16:
                len_iv_str = '0%s' % str(hex(self._write_cip.iv_lenght))[2]
            else:
                len_iv_str = str(hex(self._write_cip.iv_lenght))[2:4]
            self._fh.write('%s%s' % (len_iv_str, self._write_cip.iv))

    ## Read from encrypted file
    # @param block_size (int) size of block for reading
    #
    # will be applied only if open in read (decrypt)
    #
    def read(self, block_size):
        block = self._fh.read(block_size)
        if len(block) > len(self._iv_read):
            return self._read_cip.update(block)
        elif not self._did_final_read:
            self._did_final_read = True
            return self._read_cip.doFinal(block)
        return ''

    ## Write to encrypted file
    # @param block (str) a block to write
    #
    # will be applied only if open in write (encrypt)
    #
    def write(self, block):
        self._fh.write(self._write_cip.update(block))

    ## close the encrypted file
    def close(self):
        if self._write_cip is not None:
            self._fh.write(self._write_cip.doFinal())
        self._fh.close()


## support with for CodeFile
#
# handelling 'with' support
#
class MyOpen(object):

    ## Constructor
    def __init__(self, code_file, read_or_write):
        self._code_file = code_file
        self._read_or_write = read_or_write

    ## the start of 'with'
    def __enter__(self):
        self._code_file.open(self._read_or_write)
        return self._code_file

    ## the end of 'with'
    def __exit__(self, type, value, traceback):
        self._code_file.close()
