#
## @package MSecret.crypte ciphers module.
## @file crypte.py Implementation of @ref MSecret.crypte
#


import pyaes
import hashlib
import os
import struct


## MyCipher - my encryption
#
# creates block encryption, encrypt and decrypt data 
#
class MyCipher(object):

    ## tail - padding that left in block
    _tail = ''
    _64bitstruct = struct.Struct('Q')

    ## encrypting block
    # @param ciphered (string) text to encrypt\decrypt.
    # @returns (tuple) updated block, rest of tail
    #
    def _update(self, ciphered):
        first_bytes = ciphered[:self._64bitstruct.size]
        rest = ciphered[self._64bitstruct.size:]
        block = self._64bitstruct.pack(
            self._key ^ self._extra_key ^ self._64bitstruct.unpack(
                first_bytes,
            )[0],
        )
        self._extra_key = self._64bitstruct.unpack(
            block if self._encrypt else first_bytes,
        )[0]
        return block, rest

    ## Constructor
    def __init__(
        self,
        password,
        encrypt,
        iv=None,
    ):
        self._encrypt = encrypt
        ## key - 64 last bit of hash of password
        self._key = self._64bitstruct.unpack(
            hashlib.sha1(
                password
            ).hexdigest()[-self._64bitstruct.size:]
        )[0]
        if iv is None:
            if encrypt:
                self._iv = os.urandom(self._64bitstruct.size)
            else:
                raise ValueError("Can't decrypt data without the iv.")
        else:
            if not len(iv) == self._64bitstruct.size:
                raise ValueError('iv lenght is not 8')
            self._iv = iv
        self._extra_key = self._64bitstruct.unpack(self._iv)[0]

    ## Retrive iv lenght
    @property
    def iv_lenght(self):
        return self._64bitstruct.size

    ## Retrive iv
    @property
    def iv(self):
        return self._iv

    ## encrypt\decrypt data by blocks
    # @param data (string) data to update
    # @return (string) updated data (without padding)
    #
    def update(self, data):
        self._tail += data
        answer = ''
        while len(self._tail) > self._64bitstruct.size:
            tmp, self._tail = self._update(self._tail)
            answer += tmp
        return answer

    ## handling padding
    # @param data (string) data to update
    # @return (string) updated data include padding
    #
    def doFinal(self, data=''):
        answer = self.update(data)
        if self._encrypt:
            if len(self._tail) == self._64bitstruct.size:
                tmp, self._tail = self._update(self._tail)
                answer += tmp
            tmp = hex(self._64bitstruct.size - len(self._tail) - 1)[2]
            padding = self._tail + os.urandom(
                self._64bitstruct.size - 1 - len(
                    self._tail,
                ),
            ) + '%s' % tmp
            answer += self._update(padding)[0]
        else:
            if not len(self._tail) == self._64bitstruct.size:
                raise ValueError('Wrong data or problem with encryption')
            padding = self._update(self._tail)[0]
            answer += padding[:-int(padding[-1], 16) - 1]
        return answer


## AESCipher - AES encryption
#
# creates block encryption, encrypt and decrypt data 
#
class AesCipher(object):
    ## tail - padding that left in block
    _tail = ''
    _128bit = 16

     ## Constructor
    def __init__(
        self,
        password,
        encrypt,
        iv=None,
    ):
        self._encrypt = encrypt
        ## key - 128 last bit of password
        key = hashlib.sha1(
            password
        ).hexdigest()[-self._128bit:]
        if iv is None:
            self._iv = os.urandom(self._128bit)
        else:
            if not len(iv) == self._128bit:
                raise ValueError('IV lenght is not 16')
            self._iv = iv
        self._aes = pyaes.AESModeOfOperationCBC(key, self._iv)

    ## Retrive iv lenght
    @property
    def iv_lenght(self):
        return self._128bit

    ## Retrive iv
    @property
    def iv(self):
        return self._iv

    ## encrypt\decrypt data by blocks
    # @param data (string) data to update
    # @return (string) updated data (without padding)
    #
    def update(self, data):
        self._tail += data
        answer = ''
        while len(self._tail) > self._128bit:
            if self._encrypt:
                answer += self._aes.encrypt(self._tail[:16])
            else:
                answer += self._aes.decrypt(self._tail[:16])
            self._tail = self._tail[16:]
        return answer

    ## handling padding
    # @param data (string) data to update
    # @return (string) updated data include padding
    #
    def doFinal(self, data=''):
        answer = self.update(data)
        if self._encrypt:
            if len(self._tail) == self._128bit:
                answer += self._aes.encrypt(self._tail)
                self._tail = ''
            tmp = hex(self._128bit - len(self._tail) - 1)[2]
            padding = self._tail + os.urandom(
                self._128bit - 1 - len(
                    self._tail,
                ),
            ) + '%s' % tmp
            answer += self._aes.encrypt(padding)
        else:
            if not len(self._tail) == self._128bit:
                raise ValueError('Wrong data or problem with encryption')
            padding = self._aes.decrypt(self._tail)
            answer += padding[:-int(padding[-1], 16) - 1]
        return answer
