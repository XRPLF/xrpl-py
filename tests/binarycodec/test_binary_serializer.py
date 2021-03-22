from unittest import TestCase

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.binary_wrappers.binary_serializer import BinarySerializer
from xrpl.core.binarycodec.types.blob import Blob


class TestBinarySerializer(TestCase):
    # This is currently a sanity check for private _encode_variable_length_prefix,
    # which is called by BinarySerializer.write_length_encoded
    def test_write_length_encoded(self):
        # length ranges: 0 - 192, 193 - 12480, 12481 - 918744
        for case in [100, 1000, 20_000]:
            bytestring = "A2" * case
            blob = Blob.from_value(bytestring)
            self.assertEqual(len(blob), case)  # sanity check
            binary_serializer = BinarySerializer()
            binary_serializer.write_length_encoded(blob)

            binary_parser = BinaryParser(bytes(binary_serializer).hex())
            decoded_length = binary_parser._read_length_prefix()
            self.assertEqual(case, decoded_length)
