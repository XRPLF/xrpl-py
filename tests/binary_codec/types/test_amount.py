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
