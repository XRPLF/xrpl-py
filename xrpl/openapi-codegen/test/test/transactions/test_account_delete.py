import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.account_delete import AccountDelete

class TestAccountDelete(unittest.TestCase):
    def test_tx_invalid_missing_required_param_destination(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountDelete(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               credential_ids=[
                   "AAAAA"
               ],
               destination_tag=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_credential_ids_less_than_min_items(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountDelete(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               credential_ids=[
               ],
               destination="AAAAA",
               destination_tag=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_credential_ids_more_than_max_items(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountDelete(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               credential_ids=[
                   "AAAAA",
                   "BBBBB",
                   "CCCCC",
                   "DDDDD",
                   "EEEEE",
                   "FFFFF",
                   "GGGGG",
                   "HHHHH",
                   "IIIII"
               ],
               destination="AAAAA",
               destination_tag=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountDelete(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               credential_ids=[
                   "AAAAA"
               ],
               destination="AAAAA",
               destination_tag=5
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = AccountDelete(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            credential_ids=[
                "AAAAA"
            ],
            destination="AAAAA",
            destination_tag=5
        )
        self.assertTrue(tx.is_valid())
