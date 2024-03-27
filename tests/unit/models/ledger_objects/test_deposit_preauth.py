from unittest import TestCase

from xrpl.models.ledger_objects.deposit_preauth import DepositPreauth
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestDepositPreauth(TestCase):
    def test_deposit_preauth(self):
        deposit_preauth_json = {
            "LedgerEntryType": "DepositPreauth",
            "Account": "rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
            "Authorize": "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            "Flags": 0,
            "OwnerNode": "0000000000000000",
            "PreviousTxnID": "3E8964D5A86B3CD6B9ECB33310D4E073D64C865A5B866200"
            "AD2B7E29F8326702",
            "PreviousTxnLgrSeq": 7,
            "index": "4A255038CC3ADCC1A9C91509279B59908251728D0DAADB248FFE297D0F7E068C",
        }
        actual = LedgerObject.from_xrpl(deposit_preauth_json)
        expected = DepositPreauth(
            index="4A255038CC3ADCC1A9C91509279B59908251728D0DAADB248FFE297D0F7E068C",
            account="rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
            authorize="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            owner_node="0000000000000000",
            previous_txn_id="3E8964D5A86B3CD6B9ECB33310D4E073D64C8"
            "65A5B866200AD2B7E29F8326702",
            previous_txn_lgr_seq=7,
        )
        self.assertEqual(actual, expected)
