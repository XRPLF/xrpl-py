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
    A test utility to calculate the length specified by the given length_prefix,
    as described in https://xrpl.org/serialization.html#length-prefixing.
    """
    if len(length_prefix_bytes) == 1:
        """
        If the field contains 0 to 192 bytes of data, the first byte defines
        the length of the contents
        """
        return length_prefix_bytes[0]
    elif len(length_prefix_bytes) == 2:
        """
        If the field contains 193 to 12480 bytes of data, the first two bytes
        indicate the length of the field with the following formula:
            193 + ((byte1 - 193) * 256) + byte2
        """
        return 193 + ((length_prefix_bytes[0] - 193) * 256) + length_prefix_bytes[1]
    elif len(length_prefix_bytes) == 3:
        """
        If the field contains 12481 to 918744 bytes of data, the first three
        bytes indicate the length of the field with the following formula:
            12481 + ((byte1 - 241) * 65536) + (byte2 * 256) + byte3
        """
        return (
            12481
            + ((length_prefix_bytes[0] - 241) * 65536)
            + (length_prefix_bytes[1] * 256)
            + length_prefix_bytes[2]
        )
    raise Exception("Length prefix must contain between 1 and 3 bytes.")
