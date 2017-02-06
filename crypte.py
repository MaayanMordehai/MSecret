
import hashlib
import os
import random
import string
import struct


BLOCK_SIZE = 1024


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

    _tail = ''
    
    def _update(self, ciphered):
        print '\n\n\n%s\n\n\n' % ciphered
        x, y = ciphered[:8], ciphered[8:]
        block = struct.pack(
            'Q',
            self._key ^ self._extra_key ^ struct.unpack(
                'Q',
                x,
            )[0],
        )
        self._extra_key = struct.unpack(
            'Q',
            block if self._encrypt else x,
        )[0]
        return block, y

    def __init__(
        self,
        password,
        encrypt,
        iv=None,
    ): # MAX IV - FF
        # key - 64 last bit of password
        self._encrypt = encrypt
        self._key = struct.unpack(
            'Q',
            hashlib.sha1(
                password
            ).hexdigest()[-8:]
        )[0]
        # tail - padding that left in block
        # encrypt or decrypt
        if iv is None:
            self._iv = os.urandom(8)
        else:
            self._iv = iv
        self._extra_key = struct.unpack('Q', self._iv)[0]

    def get_iv_lenght(self):
        return len(self._iv) 

    def get_iv(self): 
        return self._iv

    def update(self, data):
        self._tail += data
        answer = ''
        while len(self._tail) > 8:
            x, self._tail = self._update(self._tail)
            print "\n\n\n%s\n\n\n" % self._tail
            answer += x
        print "a " + answer
        return answer

    def doFinal(self, data=''):
        answer = self.update(data)
        # padding - 1 to 8 random bytes with last byte implies padding size,
        # can be 1-8
        if not self._encrypt:
            print "td: " + self._tail
            padding = self._update(self._tail)[0]
            answer += padding[:-int(padding[-1])]
            print answer
        else:
            print "te: "+self._tail
            if len(self._tail) == 8:
                x, self._tail = self._update(self._tail)
                answer += x
            padding = self._tail + os.urandom(
                7 - len(
                self._tail,
                ),
            ) + '%s' % (
                8 - len(
                    self._tail,
                ),
            )
            answer += self._update(padding)[0]
        print "ananannana: "+ answer
        return answer


def main():
    en = ''
    print "hello"
    de = ''
    c = MyCipher("shachar123", True)
    f = c.update('hhhhhhhh')
    f += c.doFinal()
    print "this: %s" % len(f)
    c2 =  MyCipher("shachar123", False, c.get_iv())
    f2 = c2.update(f)
    f2 += c2.doFinal()
    print ''
    print ''
    print ''
    print ''
    print "this2: %s" % f2
    print ''
    print ''
    print ''
    print ''
    for i in ["jksfhg", "hhhhhhhh", "hhh", "q", "akernjsnbdkjgndbweha"]:
        a = ''
        de = ''
        c = MyCipher("shachar123", True)
        if c.get_iv_lenght() < 16:
            de = '0' + str(hex(c.get_iv_lenght()))[2]
        else:
            de = str(hex(c.get_iv_lenght()))[2:4]
        de += c.get_iv()
        print i
        for j in i:
            print j
            de += c.update(j)
        de += c.doFinal()
        print "de - en : "+de
        iv = de[2 : 2 + int(de[0:2])]
        de = de[int(de[0 : 2]) + 2 :]
        c2 = MyCipher("shachar123", False, iv)
        for n in de:
            a += c2.update(n)
        a += c2.doFinal()
        print a
        print a == i

if __name__ == '__main__':
    main()
