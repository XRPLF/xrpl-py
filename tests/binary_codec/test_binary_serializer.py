import unittest

from xrpl.binary_codec.binary_wrappers.binary_serializer import BinarySerializer


class TestBinarySerializer(unittest.TestCase):
    # TODO: update this test when write_length_encoded is fully complete.
    # This is currently a sanity check for private _encode_variable_length_prefix,
    # which is called by BinarySerializer.write_length_encoded
    def test_write_length_encoded(self):
        # length ranges: 0 - 192, 193 - 12480, 12481 - 918744
        for case in [100, 1000, 20_000]:
            binary_serializer = BinarySerializer()
            binary_serializer.write_length_encoded(case)
            decoded_length = calculate_length_from_prefix(binary_serializer.bytesink)
            self.assertEqual(case, decoded_length)


# TODO: (amiecorso) can replace this with BinaryParser's
# read_variable_length_length once implemented.
def calculate_length_from_prefix(length_prefix_bytes):
    """
    A test utility to calculate the length specified by the given length_prefix,
    as described in https://xrpl.org/serialization.html#length-prefixing.
    """
    if len(length_prefix_bytes) == 1:
        # If the field contains 0 to 192 bytes of data, the first byte defines
        # the length of the contents
        return length_prefix_bytes[0]
    if len(length_prefix_bytes) == 2:
        # If the field contains 193 to 12480 bytes of data, the first two bytes
        # indicate the length of the field with the following formula:
        #    193 + ((byte1 - 193) * 256) + byte2
        return 193 + ((length_prefix_bytes[0] - 193) * 256) + length_prefix_bytes[1]
    if len(length_prefix_bytes) == 3:
        # If the field contains 12481 to 918744 bytes of data, the first three
        # bytes indicate the length of the field with the following formula:
        #    12481 + ((byte1 - 241) * 65536) + (byte2 * 256) + byte3
        return (
            12481
            + ((length_prefix_bytes[0] - 241) * 65536)
            + (length_prefix_bytes[1] * 256)
            + length_prefix_bytes[2]
        )
    raise Exception("Length prefix must contain between 1 and 3 bytes.")
