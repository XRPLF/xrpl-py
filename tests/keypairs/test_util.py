import unittest

from xrpl.keypairs import util

class TestUtil(unittest.TestCase):

    def test_bytes_to_hex(self):
        output = util.bytes_to_hex(b"hi")
        self.assertEqual(type(output), bytes)

    def test_hex_to_bytes(self):
        output = util.hex_to_bytes(b"6869")
        self.assertEqual(type(output), bytes)

    def test_compute_public_key_hash(self):
        output = util.compute_public_key_hash(b"hi")
        self.assertEqual(type(output), bytes)
