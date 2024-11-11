from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import Clawback

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_XRP_AMOUNT = "1000"
_ISSUED_CURRENCY_AMOUNT = IssuedCurrencyAmount(
    currency="BTC", value="1.002", issuer=_ACCOUNT
)
_MPT_AMOUNT = MPTAmount(
    mpt_issuance_id="000004C463C52827307480341125DA0577DEFC38405B0E3E", value="10"
)


class TestClawback(TestCase):
    def test_amount_is_XRP(self):
        with self.assertRaises(XRPLModelException):
            Clawback(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
            )

    def test_holder_is_issuer(self):
        with self.assertRaises(XRPLModelException):
            Clawback(
                account=_ACCOUNT,
                amount=_ISSUED_CURRENCY_AMOUNT,
            )

    def test_cannot_holder(self):
        with self.assertRaises(XRPLModelException):
            Clawback(
                account=_ACCOUNT,
                amount=_ISSUED_CURRENCY_AMOUNT,
                holder=_ACCOUNT,
            )

    def test_invalid_holder(self):
        with self.assertRaises(XRPLModelException):
            Clawback(
                account=_ACCOUNT,
                amount=_MPT_AMOUNT,
                holder=_ACCOUNT,
            )

    def test_missing_holder(self):
        with self.assertRaises(XRPLModelException):
            Clawback(
                account=_ACCOUNT,
                amount=_MPT_AMOUNT,
            )
