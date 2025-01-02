from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowFinish
from xrpl.models.utils import MAX_CREDENTIAL_ARRAY_LENGTH

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_OFFER_SEQUENCE = 1
_OWNER = "rJZdUusLDtY9NEsGea7ijqhVrXv98rYBYN"
_SEQUENCE = 19048


class TestEscrowFinish(TestCase):
    def test_fulfillment_set_condition_unset(self):
        fulfillment = "fulfillment"

        with self.assertRaises(XRPLModelException):
            EscrowFinish(
                account=_ACCOUNT,
                fee=_FEE,
                fulfillment=fulfillment,
                offer_sequence=_OFFER_SEQUENCE,
                owner=_OWNER,
                sequence=_SEQUENCE,
            )

    def test_condition_set_fulfillment_unset(self):
        condition = "condition"

        with self.assertRaises(XRPLModelException):
            EscrowFinish(
                account=_ACCOUNT,
                condition=condition,
                fee=_FEE,
                offer_sequence=_OFFER_SEQUENCE,
                owner=_OWNER,
                sequence=_SEQUENCE,
            )

    def test_creds_list_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                offer_sequence=1,
                credential_ids=[
                    "credential_index_" + str(i)
                    for i in range(MAX_CREDENTIAL_ARRAY_LENGTH + 1)
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot exceed "
            + str(MAX_CREDENTIAL_ARRAY_LENGTH)
            + " elements.'}",
        )

    def test_creds_list_duplicates(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                offer_sequence=1,
                credential_ids=["credential_index" for _ in range(5)],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids_duplicates': 'CredentialIDs list cannot contain duplicate"
            + " values.'}",
        )

    def test_creds_list_empty(self):
        with self.assertRaises(XRPLModelException) as err:
            EscrowFinish(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                offer_sequence=1,
                credential_ids=[],
            )
        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot be empty.'}",
        )

    def test_valid(self):
        tx = EscrowFinish(
            account=_ACCOUNT,
            owner=_ACCOUNT,
            offer_sequence=1,
            credential_ids=[
                "EA85602C1B41F6F1F5E83C0E6B87142FB8957BD209469E4CC347BA2D0C26F66A"
            ],
        )
        self.assertTrue(tx.is_valid())
