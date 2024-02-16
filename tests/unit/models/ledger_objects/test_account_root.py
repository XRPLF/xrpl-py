from unittest import TestCase

from xrpl.models.ledger_objects.account_root import AccountRoot
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestAccountRoot(TestCase):
    def test_account_root(self):
        account_root_json = {
            "Account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            "AccountTxnID": "0D5FB50FA65C9FE1538FD7E398FFFE9D190"
            "8DFA4576D8D7A020040686F93C77D",
            "Balance": "148446663",
            "Domain": "6D64756F31332E636F6D",
            "EmailHash": "98B4375E1D753E5B91627516F6D70977",
            "Flags": 8388608,
            "LedgerEntryType": "AccountRoot",
            "MessageKey": "0000000000000000000000070000000300",
            "OwnerCount": 3,
            "NFTokenMinter": "rHello",
            "PreviousTxnID": "0D5FB50FA65C9FE1538FD7E398FFFE9D1908DFA4576D8D7A0200"
            "40686F93C77D",
            "PreviousTxnLgrSeq": 14091160,
            "Sequence": 336,
            "TransferRate": 1004999999,
            "index": "13F1A95D7AAB7108D5CE7EEAF504B2894B8C674E6D68499076441C4837282BF8",
        }
        actual = LedgerObject.from_xrpl(account_root_json)
        expected = AccountRoot(
            index="13F1A95D7AAB7108D5CE7EEAF504B2894B8C674E6D68499076441C4837282BF8",
            account="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            balance="148446663",
            flags=8388608,
            owner_count=3,
            previous_txn_id="0D5FB50FA65C9FE1538FD7E398FFFE9D"
            "1908DFA4576D8D7A020040686F93C77D",
            previous_txn_lgr_seq=14091160,
            sequence=336,
            account_txn_id="0D5FB50FA65C9FE1538FD7E398FFFE9D1"
            "908DFA4576D8D7A020040686F93C77D",
            domain="6D64756F31332E636F6D",
            email_hash="98B4375E1D753E5B91627516F6D70977",
            message_key="0000000000000000000000070000000300",
            nftoken_minter="rHello",
            transfer_rate=1004999999,
        )
        self.assertEqual(actual, expected)
