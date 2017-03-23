import crypte
import os


class CodeFile(object):
    '''class that represent the encrypted file'''

    def __init__(self, file_name, password):
        self._file_name = file_name
        self._fd = None
        self._password = password
        self._iv_read = None
        self._read_cip = None
        self._write_cip = None
        self._did_final_read = False

    def open(self, read_or_write):
        if read_or_write == 'r':
            self._fd = os.open(
                self._file_name,
                os.O_RDONLY,
                0o0666,
            )
        elif read_or_write == 'w':
            self._fd = os.open(
                self._file_name,
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                0o0666,
            )
        elif read_or_write == 'rw':
            self._fd = os.open(
                self._file_name,
                O_RDWR | os.O_CREAT | os.O_TRUNC,
                0o0666,
            )

    def _read_block(self, block_size):
        '''
        fd - the file descriptor of the file we want to read
        block_size - the number of bytes we want to read

        reading from file a block

        returning the text - what we read from file
        '''
        text = ''
        tmp = ''
        while True:
            tmp = os.read(self._fd, block_size)
            text += tmp
            if len(text) == block_size or not tmp:
                break
        return text

    def read(self, block_size):
        if self._iv_read is None:
            self._iv_read = self._read_block(int(self._read_block(2), 16))
            self._read_cip = crypte.MyCipher(
                self._password,
                False,
                self._iv_read,
            )
        block = self._read_block(block_size)
        if len(block) < block_size and block:
            return self._read_cip.doFinal(block)
        elif block:
            return self._read_cip.update(block)
        elif self._did_final_read:
            return self._read_cip.doFinal()
            self._did_final_read = True
        return block

    def _my_write(self, data):
        while data:
            data = data[os.write(self._fd, data):]

    def write(self, block):
        if self._write_cip is None:
            self._write_cip = crypte.MyCipher(
                self._password,
                True,
            )
            if self._write_cip.iv_lenght < 16:
                len_iv_str = '0' + str(hex(self._write_cip.iv_lenght))[2]
            else:
                len_iv_str = str(hex(self._write_cip.iv_lenght))[2:4]
            self._my_write(len_iv_str + self._write_cip.iv)

        self._my_write(self._write_cip.update(block))

    def close(self):
        if self._write_cip:
            self._my_write(self._write_cip.doFinal())
        os.close(self._fd)


class MyOpen(object):

    def __init__(self, code_file, read_or_write):
        self._code_file = code_file
        self._read_or_write = read_or_write

    def __enter__(self):
        self._code_file.open(self._read_or_write)
        return self._code_file

    def __exit__(self, type, value, traceback):
        self._code_file.close()


