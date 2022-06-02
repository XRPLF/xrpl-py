from unittest import TestCase

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.st_array import _ARRAY_END_MARKER, STArray

MEMO = {
    "Memo": {
        "MemoType": "687474703A2F2F6578616D706C652E636F6D2F6D656D6F2F67656E65726963",
        "MemoData": "72656E74",
    }
}
MEMO_HEX = (
    "EA7C1F687474703A2F2F6578616D706C652E636F6D2F6D656D6F2F67656E657269637D0472656E74E1"
)

EXPECTED_JSON = [MEMO, MEMO]

BUFFER = MEMO_HEX + MEMO_HEX + _ARRAY_END_MARKER.hex().upper()


class TestSTArray(TestCase):
    maxDiff = 1000

    def test_from_value(self):
        serialized_list = STArray.from_value(EXPECTED_JSON)
        self.assertEqual(BUFFER, str(serialized_list))

    def test_from_parser(self):
        parser = BinaryParser(BUFFER)
        serialized_list = STArray.from_parser(parser)
        self.assertEqual(BUFFER, str(serialized_list))

    def test_from_value_to_json(self):
        serialized_list = STArray.from_value(EXPECTED_JSON)
        actual_json = serialized_list.to_json()
        self.assertEqual(actual_json[0], actual_json[1])
        self.assertEqual(actual_json, EXPECTED_JSON)

    def test_from_parser_to_json(self):
        parser = BinaryParser(BUFFER)
        serialized_list = STArray.from_parser(parser)
        self.assertEqual(serialized_list.to_json(), EXPECTED_JSON)

    def test_from_value_non_list(self):
        obj = 123
        with self.assertRaises(XRPLBinaryCodecException):
            STArray.from_value(obj)

    def test_from_value_bad_list(self):
        obj = [123]
        with self.assertRaises(XRPLBinaryCodecException):
            STArray.from_value(obj)

    def test_raises_invalid_value_type(self):
        invalid_value = 1
        self.assertRaises(
            XRPLBinaryCodecException,
            STArray.from_value,
            invalid_value,
        )
