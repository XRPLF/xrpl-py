from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import Clawback

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_XRP_AMOUNT = "1000"
_ISSUED_CURRENCY_AMOUNT = IssuedCurrencyAmount(
    currency="BTC", value="1.002", issuer=_ACCOUNT
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
