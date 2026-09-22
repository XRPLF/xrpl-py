from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_send import ConfidentialMPTSend

_SENDER = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_DESTINATION = "rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9"
_MPTOKEN_ISSUANCE_ID = "0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47"
# Issuance IDs whose embedded issuer is _SENDER (204288D2..09711) / a valid
# destination rHb9... (B5F762..37E8), used for the issuer-role-ban tests.
_ISSUER_IS_SENDER_ID = "0000012F204288D2E47F8EF6C99BCC457966320D12409711"
_ISSUER_IS_DEST_ID = "0000012FB5F762798A53D543A014CAF8B297CFF8F2F937E8"
_DEST_IS_ISSUER = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
_VALID_CIPHERTEXT = "A" * 132  # 66 bytes (two compressed EC points)
_VALID_COMMITMENT = "B" * 66  # 33 bytes (one compressed EC point)
_VALID_SEND_PROOF = "C" * 1892  # 946 bytes: sigma (192) + double bulletproof (754)


class TestConfidentialMPTSend(TestCase):
    def test_valid_send(self):
        tx = ConfidentialMPTSend(
            account=_SENDER,
            destination=_DESTINATION,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            sender_encrypted_amount=_VALID_CIPHERTEXT,
            destination_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            zk_proof=_VALID_SEND_PROOF,
            amount_commitment=_VALID_COMMITMENT,
            balance_commitment=_VALID_COMMITMENT,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_account_is_issuer(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_ISSUER_IS_SENDER_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'account': 'The issuer cannot be the sender of a Send'}",
        )

    def test_invalid_destination_is_issuer(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DEST_IS_ISSUER,
                mptoken_issuance_id=_ISSUER_IS_DEST_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'destination': 'The issuer cannot be the destination of a Send'}",
        )

    def test_invalid_empty_credential_ids(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
                credential_ids=[],
            )
        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot be empty.'}",
        )

    def test_valid_send_with_auditor(self):
        tx = ConfidentialMPTSend(
            account=_SENDER,
            destination=_DESTINATION,
            mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
            sender_encrypted_amount=_VALID_CIPHERTEXT,
            destination_encrypted_amount=_VALID_CIPHERTEXT,
            issuer_encrypted_amount=_VALID_CIPHERTEXT,
            zk_proof=_VALID_SEND_PROOF,
            amount_commitment=_VALID_COMMITMENT,
            balance_commitment=_VALID_COMMITMENT,
            auditor_encrypted_amount=_VALID_CIPHERTEXT,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_sender_equals_destination(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_SENDER,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'destination': 'Sender cannot send to themselves'}",
        )

    def test_invalid_sender_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount="A" * 100,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'sender_encrypted_amount': "
            "'sender_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_destination_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount="A" * 300,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'destination_encrypted_amount': "
            "'destination_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_issuer_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount="A" * 50,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'issuer_encrypted_amount': "
            "'issuer_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_auditor_encrypted_amount_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
                auditor_encrypted_amount="A" * 100,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'auditor_encrypted_amount': "
            "'auditor_encrypted_amount must be 66 bytes (132 hex characters)'}",
        )

    def test_invalid_amount_commitment_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment="B" * 32,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'amount_commitment': "
            "'amount_commitment must be 33 bytes (66 hex characters)'}",
        )

    def test_invalid_balance_commitment_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment="B" * 200,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'balance_commitment': "
            "'balance_commitment must be 33 bytes (66 hex characters)'}",
        )

    def test_invalid_zk_proof_length(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id=_MPTOKEN_ISSUANCE_ID,
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof="C" * 1000,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'zk_proof': "
            "'zk_proof must be 946 bytes (1892 hex characters) for Send proof'}",
        )

    def test_invalid_mptoken_issuance_id(self):
        with self.assertRaises(XRPLModelException) as err:
            ConfidentialMPTSend(
                account=_SENDER,
                destination=_DESTINATION,
                mptoken_issuance_id="00" * 12,  # 24 hex chars, not 48
                sender_encrypted_amount=_VALID_CIPHERTEXT,
                destination_encrypted_amount=_VALID_CIPHERTEXT,
                issuer_encrypted_amount=_VALID_CIPHERTEXT,
                zk_proof=_VALID_SEND_PROOF,
                amount_commitment=_VALID_COMMITMENT,
                balance_commitment=_VALID_COMMITMENT,
            )
        self.assertEqual(
            err.exception.args[0],
            "{'mptoken_issuance_id': 'mptoken_issuance_id must be a 48-character "
            "hex string (24-byte MPTokenIssuanceID)'}",
        )
