from unittest import TestCase

from xrpl.models.currencies import MPTCurrency
from xrpl.models.exceptions import XRPLModelException

_MPTID = "00002403C84A0A28E0190E208E982C352BBD5006600555CF"


class TestMPTCurrency(TestCase):
    def test_correct_mptid_format(self):
        obj = MPTCurrency(
            mpt_issuance_id=_MPTID,
        )
        self.assertTrue(obj.is_valid())

    def test_lower_mptid_format(self):
        obj = MPTCurrency(
            mpt_issuance_id=_MPTID.lower(),
        )
        self.assertTrue(obj.is_valid())

    def test_invalid_length(self):
        with self.assertRaises(XRPLModelException):
            MPTCurrency(mpt_issuance_id=_MPTID[:40])

        with self.assertRaises(XRPLModelException):
            MPTCurrency(mpt_issuance_id=_MPTID + "AA")

    def test_incorrect_hex_format(self):
        # the "+" is not allowed in a currency format"
        with self.assertRaises(XRPLModelException):
            MPTCurrency(
                mpt_issuance_id="ABCD" * 11 + "XXXX",
            )

    def test_to_amount(self):
        amount = "12"
        MPT_currency = MPTCurrency(mpt_issuance_id=_MPTID)
        MPT_currency_amount = MPT_currency.to_amount(amount)

        self.assertEqual(MPT_currency_amount.mpt_issuance_id, _MPTID)
        self.assertEqual(MPT_currency_amount.value, amount)
