from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_convert import ConfidentialMPTConvert

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_MPTOKEN_ISSUANCE_ID = "000000000000000000000000" + _ACCOUNT
_VALID_CIPHERTEXT = "A" * 132  # 66 bytes (two compressed EC points)
_VALID_BLINDING_FACTOR = "B" * 64
_VALID_HOLDER_PUBLIC_KEY = "C" * 66
_VALID_SCHNORR_PROOF = "D" * 128


class TestConfidentialMPTConvert(TestCase):
    def test_valid_convert_with_registration(self):
        tx = ConfidentialMPTConvert(
            account=_ACCOUNT,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=1000,
            holder_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            blinding_factor=_VALID_BLINDING_FACTOR,
            holder_elgamal_public_key=_VALID_HOLDER_PUBLIC_KEY,
            zk_proof=_VALID_SCHNORR_PROOF,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_convert_without_registration(self):
        tx = ConfidentialMPTConvert(
            account=_ACCOUNT,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=500,
            holder_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            blinding_factor=_VALID_BLINDING_FACTOR,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_mpt_amount_zero(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=0,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount cannot be zero or negative'}",
        )

    def test_invalid_mpt_amount_negative(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=-100,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mpt_amount': 'mpt_amount cannot be zero or negative'}",
        )

    def test_invalid_holder_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount="A" * 100,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'holder_encrypted_amount': "
            "'holder_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_issuer_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount="A" * 300,
                blinding_factor=_VALID_BLINDING_FACTOR,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'issuer_encrypted_amount': "
            "'issuer_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_auditor_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                auditor_encrypted_amount="A" * 100,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'auditor_encrypted_amount': "
            "'auditor_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_blinding_factor_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor="B" * 32,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'blinding_factor': "
            "'blinding_factor must be 32 bytes (64 hex characters)'}",
        )

    def test_invalid_holder_public_key_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                holder_elgamal_public_key="C" * 50,
                zk_proof=_VALID_SCHNORR_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'holder_elgamal_public_key': "
            "'holder_elgamal_public_key must be 33 bytes (66 hex characters)'}",
        )

    def test_invalid_zk_proof_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                holder_elgamal_public_key=_VALID_HOLDER_PUBLIC_KEY,
                zk_proof="D" * 100,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof must be 64 bytes (128 hex characters) for Schnorr Proof'}",
        )

    def test_missing_zk_proof_with_holder_key(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                holder_elgamal_public_key=_VALID_HOLDER_PUBLIC_KEY,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof is required when registering a new holder public key'}",
        )

    def test_zk_proof_without_holder_key(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTConvert(
                account=_ACCOUNT,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                mpt_amount=1000,
                holder_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                blinding_factor=_VALID_BLINDING_FACTOR,
                zk_proof=_VALID_SCHNORR_PROOF,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof should not be provided if not registering a "
            "holder public key'}",
        )

    def test_valid_with_auditor_encrypted_amount(self):
        tx = ConfidentialMPTConvert(
            account=_ACCOUNT,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            mpt_amount=1000,
            holder_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            blinding_factor=_VALID_BLINDING_FACTOR,
            auditor_encrypted_amount=_VALID_CIPHERTEXT,
        )
        self.assertTrue(tx.is_valid())
