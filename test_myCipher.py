
import crypte
import unittest


class MyCipherTest(unittest.TestCase):

    def test(self):
        for p in "maayan", "mordehai":
            for t in 'plaintext1', 'more', '', '12345678', '123456789', '1':
                c = crypte.MyCipher(p, True)
                c2 = crypte.MyCipher(p, False, c.get_iv())
                decrypted = c2.update(c.update(t))
                self.assertEqual(t, c2.doFinal(c.doFinal()))

    def test_one_byte_at_a_time(self):
        for string in 'he', 'hjakslcm', 'pppasc pasc ', '01234567tteni`d?':
            decrypted = ''
            c = crypte.MyCipher('password', True)
            c2 = crypte.MyCipher('password', False, c.get_iv())
            for cha in string:
                decrypted += c2.update(c.update(cha))
            decrypted += c2.doFinal(c.doFinal())
            self.assertEqual(decrypted, string)

    def test_exceptions(self):
        with self.assertRaises(crypte.WrongIV):
             c = crypte.MyCipher('password', True, '123')

        with self.assertRaises(crypte.WrongIV):
            c = crypte.MyCipher('password', True, '123456789')

        with self.assertRaises(crypte.WrongDataOrProblemWithEncryption):
            c = crypte.MyCipher('password', False, '12345678')
            c.update('hello ')
            c.doFinal('world')
