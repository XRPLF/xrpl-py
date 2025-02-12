from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.permissioned_domain_delete import (
    DOMAIN_ID_LENGTH,
    PermissionedDomainDelete,
)

_ACCOUNT_1 = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestPermissionedDomainDelete(TestCase):
    def test_valid(self):
        tx = PermissionedDomainDelete(
            account=_ACCOUNT_1,
            domain_id="BC59567FA7E4078FFC501C5B6D8E4545244146982443E58177"
            "BA4DCF1AC99D6C",
        )
        self.assertTrue(tx.is_valid())

    def test_domain_id_too_short(self):
        with self.assertRaises(XRPLModelException) as err:
            PermissionedDomainDelete(
                account=_ACCOUNT_1,
                domain_id="BC59567FA7E4078FFC501C5B6D8",
            )

        self.assertEqual(
            err.exception.args[0],
            "{'PermissionedDomainDelete': 'domain_id must be "
            f"{DOMAIN_ID_LENGTH} characters long.'}}",
        )

    def test_domain_id_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            PermissionedDomainDelete(
                account=_ACCOUNT_1,
                domain_id="BC59567FA7E4078FFC501C5B6D8E4545244146982443E58177"
                "BA4DCF1AC99D6C1",
            )

        self.assertEqual(
            err.exception.args[0],
            "{'PermissionedDomainDelete': 'domain_id must be "
            f"{DOMAIN_ID_LENGTH} characters long.'}}",
        )

    def test_domain_id_not_hex(self):
        with self.assertRaises(XRPLModelException) as err:
            PermissionedDomainDelete(
                account=_ACCOUNT_1,
                domain_id="BC59567FA7E4078FFC501C5B6D8E4545244146982443E58177"
                "BA4DCF1AC99D6G",
            )

        self.assertEqual(
            err.exception.args[0],
            "{'PermissionedDomainDelete': 'domain_id does not conform to hex format.'}",
        )
