import unittest
from decimal import Decimal

import xrpl.binary_codec.types.amount as amount
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException


class TestAmount(unittest.TestCase):
    def test_assert_xrp_is_valid(self):
        valid_zero = "0"
        valid_amount = "1000"
        invalid_amount_large = "1e20"
        invalid_amount_small = "1e-7"
        invalid_amount_decimal = "1.234"

        amount.assert_xrp_is_valid(valid_zero)
        amount.assert_xrp_is_valid(valid_amount)
        self.assertRaises(
            XRPLBinaryCodecException, amount.assert_xrp_is_valid, invalid_amount_large
        )
        self.assertRaises(
            XRPLBinaryCodecException, amount.assert_xrp_is_valid, invalid_amount_small
        )
        self.assertRaises(
            XRPLBinaryCodecException, amount.assert_xrp_is_valid, invalid_amount_decimal
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
            amount.assert_iou_is_valid(decimal)

    def test_from_value_issued_currency(self):
        # [IOU dict, expected serialized hex]
        cases = [
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
        ]
        for case in cases:
            print("CASE: ", case[0])
            amount_object = amount.Amount.from_value(case[0])
            # Convert hex to uppercase to match expectation
            self.assertEqual(amount_object.to_hex().upper(), case[1])
