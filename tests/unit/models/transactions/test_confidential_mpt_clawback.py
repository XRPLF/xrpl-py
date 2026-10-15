from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_clawback import ConfidentialMPTClawback

_ISSUER = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_HOLDER = "rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9"
# Clawback is issuer-only: the issuance ID must embed _ISSUER's AccountID
# (204288D2..09711) as its issuer — sequence(8 hex) || issuerAccountID(40 hex).
_MPTOKEN_ISSUANCE_ID = "0000012F204288D2E47F8EF6C99BCC457966320D12409711"
# A well-formed issuance ID whose issuer is NOT _ISSUER.
_MPTOKEN_ISSUANCE_ID_OTHER_ISSUER = "0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47"
_VALID_EQUALITY_PROOF = "A" * 128  # 64 bytes: compact sigma proof


class TestConfidentialMPTClawback(TestCase):
    def test_valid_clawback(self):
        tx = ConfidentialMPTClawback(
            account=_ISSUER,
            holder=_HOLDER,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=1000,
            zk_proof=_VALID_EQUALITY_PROOF,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_account_equals_holder(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_ISSUER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'holder': 'Cannot claw back from the same account'}",
        )

    def test_invalid_mpt_amount_zero(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=0,
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount cannot be zero or negative'}",
        )

    def test_invalid_mpt_amount_negative(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=-500,
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount cannot be zero or negative'}",
        )

    def test_invalid_zk_proof_length_too_short(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                zk_proof="A" * 100,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof must be 64 bytes (128 hex characters) for compact sigma proof'}",
        )

    def test_invalid_zk_proof_length_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                zk_proof="A" * 300,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof must be 64 bytes (128 hex characters) for compact sigma proof'}",
        )

    def test_invalid_mptoken_issuance_id_too_short(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id="00" * 12,  # 24 hex chars, not 48
                mpt_amount=1000,
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mptoken_issuance_id': 'mptoken_issuance_id must be a 48-character "
            "hex string (24-byte MPTokenIssuanceID)'}",
        )

    def test_invalid_mptoken_issuance_id_non_hex(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id="Z" * 48,  # 48 chars but not hex
                mpt_amount=1000,
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mptoken_issuance_id': 'mptoken_issuance_id must be a 48-character "
            "hex string (24-byte MPTokenIssuanceID)'}",
        )

    def test_valid_large_mpt_amount(self):
        tx = ConfidentialMPTClawback(
            account=_ISSUER,
            holder=_HOLDER,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=9223372036854775807,
            zk_proof=_VALID_EQUALITY_PROOF,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_mpt_amount_above_max(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=9223372036854775808,  # 2**63, over maxMPTokenAmount
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount must not exceed 9223372036854775807 "
            "(maxMPTokenAmount, 2**63 - 1)'}",
        )

    def test_invalid_account_not_issuer(self):
        # Clawback account must be the issuance's issuer.
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTClawback(
                account=_ISSUER,
                holder=_HOLDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID_OTHER_ISSUER,
                mpt_amount=1000,
                zk_proof=_VALID_EQUALITY_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'account': \"ConfidentialMPTClawback account must be "
            "the issuance's issuer\"}",
        )
