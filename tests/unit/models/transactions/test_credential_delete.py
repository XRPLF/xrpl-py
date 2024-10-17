from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.credential_delete import CredentialDelete
from xrpl.utils import str_to_hex

_ACCOUNT_ISSUER = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT_SUBJECT = "rNdY9XDnQ4Dr1EgefwU3CBRuAjt3sAutGg"
_VALID_CREDENTIAL_TYPE = str_to_hex("Passport")


class TestCredentialDelete(TestCase):
    def test_valid(self):
        tx = CredentialDelete(
            issuer=_ACCOUNT_ISSUER,
            account=_ACCOUNT_SUBJECT,
            credential_type=_VALID_CREDENTIAL_TYPE,
        )
        self.assertTrue(tx.is_valid())

        # alternative specification of the CredentialDelete transaction
        tx = CredentialDelete(
            account=_ACCOUNT_ISSUER,
            subject=_ACCOUNT_SUBJECT,
            credential_type=_VALID_CREDENTIAL_TYPE,
        )
        self.assertTrue(tx.is_valid())

    def test_unspecified_subject_and_issuer(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialDelete(
                account=_ACCOUNT_SUBJECT,
                credential_type=str_to_hex("DMV_ID"),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'invalid_params': 'CredentialDelete transaction requires at least one "
            + "input amongst issuer or subject. '}",
        )

    # invalid inputs to the credential_type field
    def test_cred_type_field_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialDelete(
                issuer=_ACCOUNT_ISSUER,
                account=_ACCOUNT_SUBJECT,
                credential_type=str_to_hex("A" * 65),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'credential_type': 'Length of credential_type field must not be greater "
            + "than 64 bytes. '}",
        )

    def test_cred_type_field_empty(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialDelete(
                issuer=_ACCOUNT_ISSUER,
                account=_ACCOUNT_SUBJECT,
                credential_type="",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'credential_type': 'Length of credential_type field must be greater than "
            + "0. credential_type field must be encoded in base-16 format. '}",
        )

    def test_cred_type_field_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialDelete(
                issuer=_ACCOUNT_ISSUER,
                account=_ACCOUNT_SUBJECT,
                credential_type="Passport",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'credential_type': 'credential_type field must be encoded in base-16 "
            + "format. '}",
        )
