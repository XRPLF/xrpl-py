from sys import maxsize
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMVote

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_AMM_ID = "24BA86F99302CF124AB27311C831F5BFAA72C4625DDA65B7EDF346A60CC19883"
_FEE_VAL = 1234


class TestAMMVote(TestCase):
    def test_trading_fee_too_high(self):
        with self.assertRaises(XRPLModelException):
            AMMVote(
                account=_ACCOUNT,
                amm_id=_AMM_ID,
                fee_val=maxsize,
            )

    def test_to_xrpl(self):
        tx = AMMVote(
            account=_ACCOUNT,
            amm_id=_AMM_ID,
            fee_val=_FEE_VAL,
        )
        expected = {
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "AMMID": _AMM_ID,
            "FeeVal": 1234,
            "TransactionType": "AMMVote",
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)
