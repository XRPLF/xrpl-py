from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_merge_inbox import (
    ConfidentialMPTMergeInbox,
)

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_MPTOKEN_ISSUANCE_ID = "0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47"
# An issuance ID whose embedded issuer IS _ACCOUNT (204288D2..09711).
_ISSUER_ISSUANCE_ID = "0000012F204288D2E47F8EF6C99BCC457966320D12409711"


class TestConfidentialMPTMergeInbox(TestCase):
    def test_valid_merge_inbox(self):
        tx = ConfidentialMPTMergeInbox(
            account=_ACCOUNT,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_account_is_issuer(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTMergeInbox(
                account=_ACCOUNT,
                mptoken_issuance_id=_ISSUER_ISSUANCE_ID,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'account': 'The issuer cannot be the account of a MergeInbox'}",
        )

    def test_invalid_mptoken_issuance_id_too_short(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTMergeInbox(
                account=_ACCOUNT,
                mptoken_issuance_id="00" * 12,  # 24 hex chars, not 48
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mptoken_issuance_id': 'mptoken_issuance_id must be a 48-character "
            "hex string (24-byte MPTokenIssuanceID)'}",
        )

    def test_invalid_mptoken_issuance_id_non_hex(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTMergeInbox(
                account=_ACCOUNT,
                mptoken_issuance_id="Z" * 48,  # 48 chars but not hex
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mptoken_issuance_id': 'mptoken_issuance_id must be a 48-character "
            "hex string (24-byte MPTokenIssuanceID)'}",
        )
