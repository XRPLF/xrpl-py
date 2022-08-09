from sys import maxsize
from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AmmCreate

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_AMM_ACCOUNT = "rPvNKfdCNj9NpNxtFtqqfqCWtVzzbKrbL7"
_IOU_ISSUER = "rPyfep3gcLzkosKC9XiE77Y8DZWG6iWDT9"
_FEE = "0.00001"


class TestAMMInstanceCreate(TestCase):
    def test_trading_fee_too_high(self):
        with self.assertRaises(XRPLModelException):
            AmmCreate(
                account=_ACCOUNT,
                amm_account=_AMM_ACCOUNT,
                fee=_FEE,
                asset1="1000",
                asset2=IssuedCurrencyAmount(
                    currency="USD", issuer=_IOU_ISSUER, value="1000"
                ),
                trading_fee=maxsize,
            )

    def test_to_xrpl(self):
        tx = AmmCreate(
            account=_ACCOUNT,
            amm_account=_AMM_ACCOUNT,
            sequence=1337,
            fee=_FEE,
            asset1="1000",
            asset2=IssuedCurrencyAmount(
                currency="USD", issuer=_IOU_ISSUER, value="1000"
            ),
            trading_fee=12,
        )
        expected = {
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "AMMAccount": "rPvNKfdCNj9NpNxtFtqqfqCWtVzzbKrbL7",
            "Asset1": "1000",
            "Asset2": {
                "currency": "USD",
                "issuer": "rPyfep3gcLzkosKC9XiE77Y8DZWG6iWDT9",
                "value": "1000",
            },
            "Fee": "0.00001",
            "TransactionType": "AmmCreate",
            "Sequence": 1337,
            "SigningPubKey": "",
            "TradingFee": 12,
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)
