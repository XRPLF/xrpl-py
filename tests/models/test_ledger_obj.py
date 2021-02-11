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
        previous_transaction_id = "1"
        previous_transaction_sequence = 1
        sequence = 1

        account_transaction_id = "id"
        domain = "domain"
        email_hash = "email_hash"
        message_key = "message_key"
        regular_key = "regular_key"
        signer_lists = []
        tick_size = 1
        transfer_rate = 1

        account_root_dict = {
            "account": account,
            "balance": balance,
            "flags": flags,
            "index": index,
            "owner_count": owner_count,
            "previous_transaction_id": previous_transaction_id,
            "previous_transaction_ledger_sequence": previous_transaction_sequence,
            "sequence": sequence,
            "account_transaction_id": account_transaction_id,
            "domain": domain,
            "email_hash": email_hash,
            "message_key": message_key,
            "regular_key": regular_key,
            "signer_lists": signer_lists,
            "tick_size": tick_size,
            "transfer_rate": transfer_rate,
        }

        account_root_object = AccountRootObject.from_dict(account_root_dict)
        expected_dict = {
            **account_root_dict,
            "type": LedgerObjectType.AccountRoot,
        }
        self.assertEqual(account_root_object.to_json(), expected_dict)
