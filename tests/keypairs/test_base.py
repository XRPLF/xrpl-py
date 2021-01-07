import unittest

from xrpl import keypairs

class TestBase(unittest.TestCase):

    def test_hash(self):
        output = keypairs.hash("hi")
        self.assertEqual(type(output), bytes)
        self.assertEqual(len(output), 32)
