import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.escrow_finish import EscrowFinish


class TestEscrowFinish(unittest.TestCase):
    def test_tx_invalid_missing_required_param_owner(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                condition="AAAAA",
                credential_ids=["AAAAA"],
                fulfillment="AAAAA",
                offer_sequence=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_mutual_presence_missing_condition(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                credential_ids=["AAAAA"],
                fulfillment="AAAAA",
                offer_sequence=5,
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_credential_ids_less_than_min_items(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                condition="AAAAA",
                credential_ids=[],
                fulfillment="AAAAA",
                offer_sequence=5,
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_credential_ids_more_than_max_items(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                condition="AAAAA",
                credential_ids=[
                    "AAAAA",
                    "BBBBB",
                    "CCCCC",
                    "DDDDD",
                    "EEEEE",
                    "FFFFF",
                    "GGGGG",
                    "HHHHH",
                    "IIIII",
                ],
                fulfillment="AAAAA",
                offer_sequence=5,
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                condition="AAAAA",
                credential_ids=["AAAAA"],
                fulfillment="AAAAA",
                offer_sequence=5,
                owner="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = EscrowFinish(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            condition="AAAAA",
            credential_ids=["AAAAA"],
            fulfillment="AAAAA",
            offer_sequence=5,
            owner="AAAAA",
        )
        self.assertTrue(tx.is_valid())
