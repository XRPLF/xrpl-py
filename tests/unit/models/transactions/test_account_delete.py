from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AccountDelete

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rf7HPydP4ihkFkSRHWFq34b4SXRc7GvPCR"


class TestAccountDelete(TestCase):
    def test_creds_list_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountDelete(
                account=_ACCOUNT,
                destination=_DESTINATION,
                credential_ids=["credential_index_" + str(i) for i in range(9)],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot have more than 8 "
            + "elements.'}",
        )

    def test_creds_list_empty(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountDelete(
                account=_ACCOUNT,
                destination=_DESTINATION,
                credential_ids=[],
            )
        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot be empty.'}",
        )

    def test_valid_account_delete_txn(self):
        tx = AccountDelete(
            account=_ACCOUNT,
            destination=_DESTINATION,
            credential_ids=[
                "EA85602C1B41F6F1F5E83C0E6B87142FB8957BD209469E4CC347BA2D0C26F66A"
            ],
        )
        self.assertTrue(tx.is_valid())
