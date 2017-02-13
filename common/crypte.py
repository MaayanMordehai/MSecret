
import hashlib
import os
import random
import string
import struct


class WrongDataOrProblemWithEncryption(RuntimeError):
    '''Exception for handeling files to decrypt which are not dividing
    in 8 - meanning wrong file or problem in encryption
    '''

    def __init__(self):
        super(
            WrongDataOrProblemWithEncryption,
            self,
        ).__init__('Wrong data or problem with encryption')


class WrongIV(RuntimeError):
    '''Exception for handeling iv which is not in lenght 8'''

    def __init__(self):
        super(WrongIV, self).__init__('IV lenght must be 8')


class MyCipher(object):
    '''Encryption - random 8  bytes of junk + for each 64 bits of data
    xor to: key (last 64 bit of hash password),
    extra_key - the last encrypted 64 bit,
    64 bit from data. at the end if data % 8 != 0
    then junk will fill the missing to 8 bytes,
    last byte is a num that says how much bytes of junk there is
    if data % 8 == 0 we will add 8 bytes - junk and last will be 8
    Decryption - remove junk, xor for same as Encryption,
    and removing the junk of last 8 bytes.
    '''

    # tail - padding that left in block
    _tail = ''
    _64bitstruct = struct.Struct('Q')


    def _update(self, ciphered):
        first_bytes, rest = ciphered[:self._64bitstruct.size], ciphered[self._64bitstruct.size:]
        block = self._64bitstruct.pack(
            self._key ^ self._extra_key ^ self._64bitstruct.unpack(
                first_bytes,
            )[0],
        )
        self._extra_key = self._64bitstruct.unpack(
            block if self._encrypt else first_bytes,
        )[0]
        return block, rest

    def __init__(
        self,
        password,
        encrypt,
        iv=None,
    ):  # MAX IV - FF
        self._encrypt = encrypt
        # key - 64 last bit of password
        self._key = self._64bitstruct.unpack(
            hashlib.sha1(
                password
            ).hexdigest()[-self._64bitstruct.size:]
        )[0]
        if iv is None:
            self._iv = os.urandom(self._64bitstruct.size)
        else:
            if not len(iv) == self._64bitstruct.size:
                raise WrongIV()
            self._iv = iv
        self._extra_key = self._64bitstruct.unpack(self._iv)[0]

    @property
    def iv_lenght(self):
        return self._64bitstruct.size

    @property
    def iv(self):
        return self._iv

    def update(self, data):
        self._tail += data
        answer = ''
        while len(self._tail) > self._64bitstruct.size:
            tmp, self._tail = self._update(self._tail)
            answer += tmp
        return answer

    def doFinal(self, data=''):
        answer = self.update(data)
        if self._encrypt:
            if len(self._tail) == self._64bitstruct.size:
                tmp, self._tail = self._update(self._tail)
                answer += tmp
            padding = self._tail + os.urandom(
                self._64bitstruct.size - 1 - len(
                    self._tail,
                ),
            ) + '%s' % (
                self._64bitstruct.size - len(
                    self._tail,
                ),
            )
            answer += self._update(padding)[0]
        else:
            if not len(self._tail) == self._64bitstruct.size:
                raise WrongDataOrProblemWithEncryption()
            padding = self._update(self._tail)[0]
            answer += padding[:-int(padding[-1])]
        return answer
