import unittest

from xrpl import binary_codec


class TestBinarySerializer(unittest.TestCase):
    def setUp(self):
        self.binary_serializer = binary_codec.BinarySerializer()

    def test_encode_variable_length_prefix(self):
        # 0 - 192, 193 - 12480, 12481 - 918744
        length_cases = [100, 1000, 20000]
        for case in length_cases:
            prefix = self.binary_serializer.encode_variable_length_prefix(case)
            decoded_length = calculate_length_from_prefix(prefix)
            self.assertEqual(case, decoded_length)


def calculate_length_from_prefix(length_prefix_bytes):
    """
    A test utility to calculate the length specified by the given length_prefix, as described
    in https://xrpl.org/serialization.html#length-prefixing.
    """
    if len(length_prefix_bytes) == 1:
        return length_prefix_bytes[0]
    elif len(length_prefix_bytes) == 2:
        return 193 + ((length_prefix_bytes[0] - 193) * 256) + length_prefix_bytes[1]
    elif len(length_prefix_bytes) == 3:
        return 12481 + ((length_prefix_bytes[0] - 241) * 65536) + (length_prefix_bytes[1] * 256) + length_prefix_bytes[2]
    raise Exception("Length prefix must contain between 1 and 3 bytes.")