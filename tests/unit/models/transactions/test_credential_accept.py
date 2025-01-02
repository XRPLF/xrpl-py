from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.utils import str_to_hex

_ISSUER = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_SUBJECT = "rNdY9XDnQ4Dr1EgefwU3CBRuAjt3sAutGg"
_VALID_CREDENTIAL_TYPE = str_to_hex("Passport")


class TestCredentialAccept(TestCase):
    def test_valid(self):
        tx = CredentialAccept(
            issuer=_ISSUER,
            account=_SUBJECT,
            credential_type=_VALID_CREDENTIAL_TYPE,
        )
        self.assertTrue(tx.is_valid())
        # Verify field values
        self.assertEqual(tx.issuer, _ISSUER)
        self.assertEqual(tx.account, _SUBJECT)
        self.assertEqual(tx.credential_type, _VALID_CREDENTIAL_TYPE)

    # invalid inputs to the credential_type field
    def test_cred_type_field_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialAccept(
                issuer=_ISSUER,
                account=_SUBJECT,
                credential_type=str_to_hex("A" * 65),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'credential_type': 'Length cannot exceed 128.'}",
        )

    def test_cred_type_field_empty(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialAccept(
                issuer=_ISSUER,
                account=_SUBJECT,
                credential_type="",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'credential_type': 'cannot be an empty string.'}",
        )

    def test_cred_type_field_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            CredentialAccept(
                issuer=_ISSUER,
                account=_SUBJECT,
                credential_type="Passport",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'credential_type': 'credential_type field must be encoded in hex.'}",
        )
