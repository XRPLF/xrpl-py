from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.confidential_mpt_send import ConfidentialMPTSend

_SENDER = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_DESTINATION = "rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9"
_MPTOKEN_ISSUANCE_ID = "000000000000000000000000" + _SENDER
_VALID_CIPHERTEXT = "A" * 132  # 66 bytes (two compressed EC points)
_VALID_COMMITMENT = "B" * 66  # 33 bytes (one compressed EC point)
_VALID_SEND_PROOF = "C" * 3006


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
            "'zk_proof must be 1503 bytes (3006 hex characters) for Send proof'}",
        )
