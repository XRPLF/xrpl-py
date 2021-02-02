import unittest

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.serialized_transaction_list import (
    ARRAY_END_MARKER,
    SerializedTransactionList,
)

memo = {
    "Memo": {
        "MemoType": "687474703a2f2f6578616d706c652e636f6d2f6d656d6f2f67656e65726963",
        "MemoData": "72656e74",
    }
}
memo_hex = (
    "EA7C1F687474703A2F2F6578616D706C652E636F6D2F6D656D6F2F67656E657269637D0472656E74E1"
)

expected_json = [memo, memo]

buffer = memo_hex + memo_hex + ARRAY_END_MARKER.hex().upper()


class TestSerializedTransactionList(unittest.TestCase):
    def test_from_value(self):
        transaction_list = SerializedTransactionList.from_value(expected_json)
        self.assertEqual(buffer, transaction_list.to_string().upper())

    def test_from_parser(self):
        parser = BinaryParser(buffer)
        transaction_list = SerializedTransactionList.from_parser(parser)
        self.assertEqual(buffer, transaction_list.to_string().upper())

    def test_from_value_to_json(self):
        transaction_list = SerializedTransactionList.from_value(expected_json)
        actual_json = transaction_list.to_json()
        self.assertEqual(actual_json[0], actual_json[1])
        self.assertEqual(actual_json, expected_json)

    def test_from_parser_to_json(self):
        parser = BinaryParser(buffer)
        transaction_list = SerializedTransactionList.from_parser(parser)
        self.assertEqual(transaction_list.to_json(), expected_json)
