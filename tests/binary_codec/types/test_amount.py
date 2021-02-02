import unittest
from decimal import Decimal

import xrpl.binary_codec.types.amount as amount
from xrpl.binary_codec.binary_wrappers import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException

# [IOU dict, expected serialized hex]
IOU_CASES = [
    [
        {
            "value": "0",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "80000000000000000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "1",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "D4838D7EA4C680000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "2",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "D4871AFD498D00000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "-2",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "94871AFD498D00000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "2.1",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "D48775F05A0740000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "currency": "XRP",
            "value": "2.1",
            "issuer": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
        },
        "D48775F05A07400000000000000000000000000000000000"
        "000000000000000000000000000000000000000000000000",
    ],
    [
        {
            "currency": "USD",
            "value": "1111111111111111",
            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
        },
        "D843F28CB71571C700000000000000000000000055534400"
        "000000000000000000000000000000000000000000000001",
    ],
]

# [XRP value, hex encoding]
XRP_CASES = [
    ["100", "4000000000000064"],
    ["100000000000000000", "416345785D8A0000"],
]


class TestAmount(unittest.TestCase):
    def test_assert_xrp_is_valid_passes(self):
        valid_zero = "0"
        valid_amount = "1000"

        amount.verify_xrp_value(valid_zero)
        amount.verify_xrp_value(valid_amount)

    def test_assert_xrp_is_valid_raises(self):
        invalid_amount_large = "1e20"
        invalid_amount_small = "1e-7"
        invalid_amount_decimal = "1.234"

        self.assertRaises(
            XRPLBinaryCodecException,
            amount.verify_xrp_value,
            invalid_amount_large,
        )
        self.assertRaises(
            XRPLBinaryCodecException,
            amount.verify_xrp_value,
            invalid_amount_small,
        )
        self.assertRaises(
            XRPLBinaryCodecException,
            amount.verify_xrp_value,
            invalid_amount_decimal,
        )

    def test_assert_iou_is_valid(self):
        # { zero, pos, negative } * fractional, large, small
        cases = [
            "0",
            "0.0",
            "1",
            "1.1111",
            "-1",
            "-1.1",
            "1111111111111111.0",
            "0.00000000001",
        ]
        for case in cases:
            decimal = Decimal(case)
            amount.verify_iou_value(decimal)

    def test_from_value_issued_currency(self):
        for json, serialized in IOU_CASES:
            amount_object = amount.Amount.from_value(json)
            # Convert hex to uppercase to match expectation
            self.assertEqual(amount_object.to_hex().upper(), serialized)

    def test_from_value_xrp(self):
        for json, serialized in XRP_CASES:
            amount_object = amount.Amount.from_value(json)
            self.assertEqual(amount_object.to_hex().upper(), serialized)

    def test_to_json_issued_currency(self):
        for json, serialized in IOU_CASES:
            parser = BinaryParser(serialized)
            amount_object = amount.Amount.from_parser(parser)
            self.assertEqual(amount_object.to_json(), json)

    def test_to_json_xrp(self):
        for json, serialized in XRP_CASES:
            parser = BinaryParser(serialized)
            amount_object = amount.Amount.from_parser(parser)
            self.assertEqual(amount_object.to_json(), json)
