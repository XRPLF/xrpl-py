from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import DepositPreauth
from xrpl.models.transactions.deposit_preauth import Credential
from xrpl.models.utils import MAX_CREDENTIAL_ARRAY_LENGTH

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestDepositPreauth(TestCase):
    def test_authorize_unauthorize_both_set(self):
        with self.assertRaises(XRPLModelException):
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize="authorize",
                unauthorize="unauthorize",
            )

    def test_authorize_unauthorize_neither_set(self):
        with self.assertRaises(XRPLModelException):
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
            )

    # unit tests using (un)/authorize_credentials input parameter
    sample_credentials = [
        Credential(issuer="SampleIssuer", credential_type="SampleCredType")
    ]

    def test_invalid_input_with_authorize_credentials(self):
        with self.assertRaises(XRPLModelException):
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize="authorize",
                authorize_credentials=self.sample_credentials,
            )

    def test_valid_input_unauthorize_credentials(self):
        tx = DepositPreauth(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            unauthorize_credentials=self.sample_credentials,
        )
        self.assertTrue(tx.is_valid())

    # Unit tests validating the length of array inputs
    def test_authcreds_array_input_exceed_length_check(self):
        sample_credentials = [
            Credential(
                issuer="SampleIssuer_" + str(i), credential_type="SampleCredType"
            )
            for i in range(MAX_CREDENTIAL_ARRAY_LENGTH + 1)
        ]

        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize_credentials=sample_credentials,
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth': '"
            + "AuthorizeCredentials list cannot exceed "
            + str(MAX_CREDENTIAL_ARRAY_LENGTH)
            + " elements. '}",
        )

    def test_auth_cred_duplicates(self):
        with self.assertRaises(XRPLModelException) as error:
            sample_credential = Credential(
                issuer="SampleIssuer", credential_type="SampleCredType"
            )
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize_credentials=[sample_credential, sample_credential],
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth': '"
            + "AuthorizeCredentials list cannot contain duplicate credentials."
            + "'}",
        )

    def test_authcreds_empty_array_inputs(self):
        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize_credentials=[],
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth': '"
            + "AuthorizeCredentials list cannot be empty. "
            + "'}",
        )

    def test_unauthcreds_array_input_exceed_length_check(self):
        sample_credentials = [
            Credential(
                issuer="SampleIssuer_" + str(i), credential_type="SampleCredType"
            )
            for i in range(MAX_CREDENTIAL_ARRAY_LENGTH + 1)
        ]

        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                unauthorize_credentials=sample_credentials,
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth': '"
            + "UnauthorizeCredentials list cannot exceed "
            + str(MAX_CREDENTIAL_ARRAY_LENGTH)
            + " elements. '}",
        )

    def test_unauthcreds_empty_array_inputs(self):
        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                unauthorize_credentials=[],
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth': '"
            + "UnauthorizeCredentials list cannot be empty. "
            + "'}",
        )
