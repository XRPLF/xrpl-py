from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import DelegateSet
from xrpl.models.transactions.delegate_set import (
    GRANULAR_PERMISSIONS,
    PERMISSION_MAX_LENGTH,
    Permission,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DELEGATED_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"


class TestAccountPermissionSet(TestCase):
    def test_delegate_set(self):
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=1)],
        )
        self.assertTrue(tx.is_valid())

    def test_delegate_set_granular_permission(self):
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[
                Permission(permission_value=GRANULAR_PERMISSIONS["PaymentMint"])
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_long_permissions_list(self):
        with self.assertRaises(XRPLModelException) as error:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(permission_value=i)
                    for i in range(PERMISSION_MAX_LENGTH + 1)
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'permissions': 'Length of `permissions` list is greater than "
            + str(PERMISSION_MAX_LENGTH)
            + ".'}",
        )

    def test_duplicate_permission_value(self):
        with self.assertRaises(XRPLModelException) as error:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(permission_value=1),
                    Permission(permission_value=1),
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'permissions': 'Duplicate permission value in `permissions` list.'}",
        )

    def test_account_and_delegate_are_the_same(self):
        with self.assertRaises(XRPLModelException) as error:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_ACCOUNT,
                permissions=[
                    Permission(permission_value=1),
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'account_addresses': 'Field `authorize` and `account` must be different."
            + "'}",
        )
