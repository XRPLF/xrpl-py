from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.deposit_preauth import Credential
from xrpl.models.transactions.permissioned_domain_set import PermissionedDomainSet
from xrpl.utils import str_to_hex

_ACCOUNT_1 = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestPermissionedDomainSet(TestCase):
    def test_valid(self):
        tx = PermissionedDomainSet(
            account=_ACCOUNT_1,
            accepted_credentials=[
                Credential(credential_type=str_to_hex("Passport"), issuer=_ACCOUNT_1)
            ],
            domain_id="BC59567FA7E4078FFC501C5B6D8E4545244146982443E58177"
            "BA4DCF1AC99D6C",
        )
        self.assertTrue(tx.is_valid())

    # tests pertaining to the length of AcceptedCredentials list
    def test_accepted_credentials_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            PermissionedDomainSet(
                account=_ACCOUNT_1,
                accepted_credentials=[
                    Credential(
                        credential_type=str_to_hex("Passport_" + str(i)),
                        issuer=_ACCOUNT_1,
                    )
                    for i in range(11)
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'PermissionedDomainSet': 'AcceptedCredentials list cannot have more than "
            + "10 elements.'}",
        )

    def test_accepted_credentials_empty(self):
        with self.assertRaises(XRPLModelException) as err:
            PermissionedDomainSet(
                account=_ACCOUNT_1,
                accepted_credentials=[],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'PermissionedDomainSet': 'AcceptedCredentials list cannot be empty.'}",
        )

    def test_accepted_credentials_contains_duplicates(self):
        with self.assertRaises(XRPLModelException) as err:
            PermissionedDomainSet(
                account=_ACCOUNT_1,
                accepted_credentials=[
                    Credential(
                        credential_type=str_to_hex("Passport"), issuer=_ACCOUNT_1
                    ),
                    Credential(
                        credential_type=str_to_hex("Passport"), issuer=_ACCOUNT_1
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'PermissionedDomainSet': 'AcceptedCredentials list cannot contain"
            + " duplicate credentials.'}",
        )
