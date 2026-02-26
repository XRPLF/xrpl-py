from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_clawback import ConfidentialMPTClawback

_ISSUER = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_HOLDER = "rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9"
_MPTOKEN_ISSUANCE_ID = "000000000000000000000000" + _ISSUER
_VALID_EQUALITY_PROOF = "A" * 196


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
            "'zk_proof must be 98 bytes (196 hex characters) for Equality Proof'}",
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
            "'zk_proof must be 98 bytes (196 hex characters) for Equality Proof'}",
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
