from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AccountPermissionSet
from xrpl.models.transactions.account_permission_set import (
    PERMISSION_MAX_SIZE,
    Permission,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DELEGATED_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"


class TestAccountPermissionSet(TestCase):
    def test_account_permission_set(self):
        tx = AccountPermissionSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=1)],
        )
        self.assertTrue(tx.is_valid())

    def test_long_permissions_list(self):
        with self.assertRaises(XRPLModelException) as error:
            AccountPermissionSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(permission_value=i)
                    for i in range(PERMISSION_MAX_SIZE + 1)
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'permissions': 'Length of `permissions` list is greater than "
            + str(PERMISSION_MAX_SIZE)
            + ".'}",
        )

    def test_duplicate_permission_value(self):
        with self.assertRaises(XRPLModelException) as error:
            AccountPermissionSet(
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
