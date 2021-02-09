import unittest

from xrpl.binarycodec.types.blob import Blob


class TestBlob(unittest.TestCase):
    def test_from_value(self):
        value = "00AA"
        value_bytes = bytes.fromhex(value)

        blob1 = Blob.from_value(value)
        blob2 = Blob(value_bytes)

        self.assertEqual(blob1.buffer, blob2.buffer)
