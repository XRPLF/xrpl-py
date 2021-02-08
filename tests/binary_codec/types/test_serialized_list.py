import unittest

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_list import _ARRAY_END_MARKER, SerializedList

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


class TestSerializedList(unittest.TestCase):
    def test_from_value(self):
        transaction_list = SerializedList.from_value(EXPECTED_JSON)
        self.assertEqual(BUFFER, transaction_list.to_string())

    def test_from_parser(self):
        parser = BinaryParser(BUFFER)
        transaction_list = SerializedList.from_parser(parser)
        self.assertEqual(BUFFER, transaction_list.to_string())

    def test_from_value_to_json(self):
        transaction_list = SerializedList.from_value(EXPECTED_JSON)
        actual_json = transaction_list.to_json()
        self.assertEqual(actual_json[0], actual_json[1])
        self.assertEqual(actual_json, EXPECTED_JSON)

    def test_from_parser_to_json(self):
        parser = BinaryParser(BUFFER)
        transaction_list = SerializedList.from_parser(parser)
        self.assertEqual(transaction_list.to_json(), EXPECTED_JSON)

    def test_from_value_non_list(self):
        obj = 123
        with self.assertRaises(XRPLBinaryCodecException):
            SerializedList.from_value(obj)

    def test_from_value_bad_list(self):
        obj = [123]
        with self.assertRaises(XRPLBinaryCodecException):
            SerializedList.from_value(obj)
