from unittest import TestCase

from xrpl.models.ledger.account_root_object import AccountRootObject
from xrpl.models.ledger.ledger_object import LedgerObjectType


class TestLedgerObj(TestCase):
    def test_from_dict(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        balance = "0.0001"
        flags = 1
        index = "ahash256"
        owner_count = 1
        previous_transaction_id = "3"
        previous_transaction_sequence = 5
        sequence = 1

        account_root_dict = {
            "account": account,
            "balance": balance,
            "flags": flags,
            "index": index,
            "owner_count": owner_count,
            "previous_transaction_id": previous_transaction_id,
            "previous_transaction_ledger_sequence": previous_transaction_sequence,
            "sequence": sequence,
        }

        obj = AccountRootObject.from_dict(account_root_dict)
        expected_dict = {**account_root_dict, "type": LedgerObjectType.AccountRoot}
        self.assertEqual(obj.owner_count, expected_dict["owner_count"])
        # obj = AccountRootObject("address", "balance", 0, "index", 0, "prv_id", 0, 0)
        # assert obj.type == "AccountRoot"
