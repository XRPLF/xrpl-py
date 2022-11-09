from sys import maxsize
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMVote

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_AMM_ID = "24BA86F99302CF124AB27311C831F5BFAA72C4625DDA65B7EDF346A60CC19883"
_TRADING_FEE = 234


class TestAMMVote(TestCase):
    def test_tx_valid(self):
        tx = AMMVote(
            account=_ACCOUNT,
            amm_id=_AMM_ID,
            trading_fee=_TRADING_FEE,
        )
        self.assertTrue(tx.is_valid())

    def test_trading_fee_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMVote(
                account=_ACCOUNT,
                amm_id=_AMM_ID,
                trading_fee=maxsize,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'trading_fee': 'Must be between 0 and 1000'}",
        )

    def test_trading_fee_negative_number(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMVote(
                account=_ACCOUNT,
                amm_id=_AMM_ID,
                trading_fee=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'trading_fee': 'Must be between 0 and 1000'}",
        )
