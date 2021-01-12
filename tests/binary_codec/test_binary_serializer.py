import unittest

from xrpl import binary_codec


class TestBinarySerializer(unittest.TestCase):
    def setUp(self):
        self.binary_serializer = binary_codec.BinarySerializer()

    def test_encode_variable_length_prefix(self):
        pass
