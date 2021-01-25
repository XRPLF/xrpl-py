import unittest

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
        pass
