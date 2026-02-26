from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_convert_back import (
    ConfidentialMPTConvertBack,
)

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_MPTOKEN_ISSUANCE_ID = "000000000000000000000000" + _ACCOUNT
_VALID_CIPHERTEXT = "A" * 132  # 66 bytes (two compressed EC points)
_VALID_COMMITMENT = "B" * 66  # 33 bytes (one compressed EC point)
_VALID_BLINDING_FACTOR = "C" * 64
_VALID_CONVERT_BACK_PROOF = "D" * 1766


class TestConfidentialMPTConvertBack(TestCase):
    def test_valid_convert_back(self):
        tx = ConfidentialMPTConvertBack(
            account=_ACCOUNT,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=1000,
            holder_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            blinding_factor=_VALID_BLINDING_FACTOR,
            balance_commitment=_VALID_COMMITMENT,
            zk_proof=_VALID_CONVERT_BACK_PROOF,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_auditor(self):
        tx = ConfidentialMPTConvertBack(
            account=_ACCOUNT,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=500,
            holder_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            blinding_factor=_VALID_BLINDING_FACTOR,
            balance_commitment=_VALID_COMMITMENT,
            zk_proof=_VALID_CONVERT_BACK_PROOF,
            auditor_encrypted_amount=_VALID_CIPHERTEXT,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_mpt_amount_zero(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=0,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount cannot be zero or negative'}",
        )

    def test_invalid_mpt_amount_negative(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=-100,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount cannot be zero or negative'}",
        )

    def test_invalid_blinding_factor_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor="C" * 32,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'blinding_factor': "
            "'blinding_factor must be 32 bytes (64 hex characters)'}",
        )

    def test_invalid_holder_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount="A" * 100,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'holder_encrypted_amount': "
            "'holder_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_issuer_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount="A" * 50,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'issuer_encrypted_amount': "
            "'issuer_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_auditor_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
                auditor_encrypted_amount="A" * 100,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'auditor_encrypted_amount': "
            "'auditor_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_balance_commitment_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment="B" * 32,
                zk_proof=_VALID_CONVERT_BACK_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'balance_commitment': "
            "'balance_commitment must be 33 bytes (66 hex characters)'}",
        )

    def test_invalid_zk_proof_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvertBack(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                balance_commitment=_VALID_COMMITMENT,
                zk_proof="D" * 1000,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof must be 883 bytes (1766 hex characters) for ConvertBack proof'}",
        )
