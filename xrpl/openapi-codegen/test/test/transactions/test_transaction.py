import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.transaction import Memo
from xrpl.models.transactions.transaction import Transaction

class TestTransaction(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            Transaction(
               account_txn_id="AAAAA",
               fee="AAAAA",
               last_ledger_sequence=5,
               memos=[
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   )
               ],
               network_id=5,
               sequence=5,
               signing_pub_key="AAAAA",
               source_tag=5,
               ticket_sequence=5,
               txn_signature="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            Transaction(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               account_txn_id="AAAAA",
               fee="AAAAA",
               last_ledger_sequence=5,
               memos=[
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   ),
                   Memo(
                       memo_data="AAAAA",
                       memo_format="AAAAA",
                       memo_type="AAAAA"
                   )
               ],
               network_id=5,
               sequence=5,
               signing_pub_key="AAAAA",
               source_tag=5,
               ticket_sequence=5,
               txn_signature="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = Transaction(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            account_txn_id="AAAAA",
            fee="AAAAA",
            last_ledger_sequence=5,
            memos=[
                Memo(
                    memo_data="AAAAA",
                    memo_format="AAAAA",
                    memo_type="AAAAA"
                ),
                Memo(
                    memo_data="AAAAA",
                    memo_format="AAAAA",
                    memo_type="AAAAA"
                ),
                Memo(
                    memo_data="AAAAA",
                    memo_format="AAAAA",
                    memo_type="AAAAA"
                ),
                Memo(
                    memo_data="AAAAA",
                    memo_format="AAAAA",
                    memo_type="AAAAA"
                ),
                Memo(
                    memo_data="AAAAA",
                    memo_format="AAAAA",
                    memo_type="AAAAA"
                )
            ],
            network_id=5,
            sequence=5,
            signing_pub_key="AAAAA",
            source_tag=5,
            ticket_sequence=5,
            txn_signature="AAAAA"
        )
        self.assertTrue(tx.is_valid())
