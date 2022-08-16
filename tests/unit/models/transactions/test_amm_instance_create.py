from sys import maxsize
from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMInstanceCreate

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_IOU_ISSUER = "rPyfep3gcLzkosKC9XiE77Y8DZWG6iWDT9"


class TestAMMInstanceCreate(TestCase):
    def test_trading_fee_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMInstanceCreate(
                account=_ACCOUNT,
                asset1="1000",
                asset2=IssuedCurrencyAmount(
                    currency="USD", issuer=_IOU_ISSUER, value="1000"
                ),
                trading_fee=maxsize,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'trading_fee': 'Must not be greater than 65000'}",
        )

    def test_to_xrpl(self):
        tx = AMMInstanceCreate(
            account=_ACCOUNT,
            asset1="1000",
            asset2=IssuedCurrencyAmount(
                currency="USD", issuer=_IOU_ISSUER, value="1000"
            ),
            trading_fee=12,
        )
        expected = {
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "Asset1": "1000",
            "Asset2": {
                "currency": "USD",
                "issuer": "rPyfep3gcLzkosKC9XiE77Y8DZWG6iWDT9",
                "value": "1000",
            },
            "TransactionType": "AMMInstanceCreate",
            "SigningPubKey": "",
            "TradingFee": 12,
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)
