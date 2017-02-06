
import hashlib
import os
import random
import string
import struct


NUM_OF_BYTES = 8


''' Exception for handeling files to decrypt which are not dividing
    in 8 - meanning wrong file or problem in encryption'''


class WrongDataOrProblemWithEncryption(RuntimeError):

    def __init__(self):
        super(
            WrongDataOrProblemWithEncryption,
            self,
        ).__init__('Wrong data or problem with encryption')


''' Exception for handeling iv which is not in lenght 8'''


class WrongIV(RuntimeError):

    def __init__(self):
        super(WrongIV, self).__init__('IV lenght must be 8')


'''  Encryption - random 8  bytes of junk + for each 64 bits of data
    xor to: key (last 64 bit of hash password),
    extra_key - the last encrypted 64 bit,
    64 bit from data. at the end if data % 8 != 0
    then junk will fill the missing to 8 bytes,
    last byte is a num that says how much bytes of junk there is
    if data % 8 == 0 we will add 8 bytes - junk and last will be 8
    Decryption - remove junk, xor for same as Encryption,
    and removing the junk of last 8 bytes.'''


class MyCipher(object):

    # tail - padding that left in block
    _tail = ''

    def _update(self, ciphered):
        first_bytes, rest = ciphered[:NUM_OF_BYTES], ciphered[NUM_OF_BYTES:]
        block = struct.pack(
            'Q',
            self._key ^ self._extra_key ^ struct.unpack(
                'Q',
                first_bytes,
            )[0],
        )
        self._extra_key = struct.unpack(
            'Q',
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
        self._key = struct.unpack(
            'Q',
            hashlib.sha1(
                password
            ).hexdigest()[-NUM_OF_BYTES:]
        )[0]
        if iv is None:
            self._iv = os.urandom(NUM_OF_BYTES)
        else:
            if not len(iv) == NUM_OF_BYTES:
                raise WrongIV()
            self._iv = iv
        self._extra_key = struct.unpack('Q', self._iv)[0]

    def get_iv_lenght(self):
        return len(self._iv)

    def get_iv(self):
        return self._iv

    def update(self, data):
        self._tail += data
        answer = ''
        while len(self._tail) > NUM_OF_BYTES:
            tmp, self._tail = self._update(self._tail)
            answer += tmp
        return answer

    def doFinal(self, data=''):
        answer = self.update(data)
        if self._encrypt:
            if len(self._tail) == NUM_OF_BYTES:
                tmp, self._tail = self._update(self._tail)
                answer += tmp
            padding = self._tail + os.urandom(
                NUM_OF_BYTES - 1 - len(
                    self._tail,
                ),
            ) + '%s' % (
                NUM_OF_BYTES - len(
                    self._tail,
                ),
            )
            answer += self._update(padding)[0]
        else:
            if not len(self._tail) == NUM_OF_BYTES:
                raise WrongDataOrProblemWithEncryption()
            padding = self._update(self._tail)[0]
            answer += padding[:-int(padding[-1])]
        return answer


def main():
    for i in ["jksfhg", "hhhhhhhh", "hhh", "q", "akernjsnbdkjgndbweha"]:
        a = ''
        de = ''
        c = MyCipher("shachar123", True)
        if c.get_iv_lenght() < 16:
            de = '0' + str(hex(c.get_iv_lenght()))[2]
        else:
            de = str(hex(c.get_iv_lenght()))[2:4]
        de += c.get_iv()
        for j in i:
            de += c.update(j)
        de += c.doFinal()
        iv = de[2: 2 + int(de[0:2])]
        de = de[int(de[0: 2]) + 2:]
        c2 = MyCipher("shachar123", False, iv)
        for n in de:
            a += c2.update(n)
        a += c2.doFinal()
        print a == i

if __name__ == '__main__':
    main()
