import unittest
import hashlib

from xrpl import keypairs

class TestBase(unittest.TestCase):
    def test_hash_uses_sha512(self):
        message = "hi"
        hasher = hashlib.sha512()
        hasher.update(bytes(message, "UTF-8"))
        sha512_expectation = hasher.digest()
        output = keypairs.hash(message)
        self.assertEqual(output, sha512_expectation[:len(output)])

    def test_hash_length_is_capped(self):
        output = keypairs.hash("hi")
        self.assertEqual(len(output), 32)
