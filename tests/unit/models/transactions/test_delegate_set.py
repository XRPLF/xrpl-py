from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import DelegateSet
from xrpl.models.transactions.delegate_set import (
    PERMISSIONS_MAX_LENGTH,
    GranularPermission,
    Permission,
)
from xrpl.models.transactions.types import TransactionType

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DELEGATED_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_MORE_THAN_10_PERMISSIONS = [
    GranularPermission.PAYMENT_MINT,
    GranularPermission.ACCOUNT_MESSAGE_KEY_SET,
    GranularPermission.ACCOUNT_TICK_SIZE_SET,
    GranularPermission.ACCOUNT_DOMAIN_SET,
    TransactionType.PAYMENT,
    TransactionType.AMM_CLAWBACK,
    TransactionType.AMM_BID,
    TransactionType.ORACLE_DELETE,
    TransactionType.MPTOKEN_AUTHORIZE,
    TransactionType.MPTOKEN_ISSUANCE_DESTROY,
    TransactionType.CREDENTIAL_ACCEPT,
]


class TestDelegateSet(TestCase):
    def test_delegate_set(self):
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[
                Permission(permission_value=GranularPermission.TRUSTLINE_AUTHORIZE),
                Permission(permission_value=TransactionType.PAYMENT),
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_delegate_set_granular_permission(self):
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=GranularPermission.PAYMENT_MINT)],
        )
        self.assertTrue(tx.is_valid())

    def test_long_permissions_list(self):
        with self.assertRaises(XRPLModelException) as error:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(permission_value=_MORE_THAN_10_PERMISSIONS[i])
                    for i in range(len(_MORE_THAN_10_PERMISSIONS))
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'permissions': 'Length of `permissions` list is greater than "
            + str(PERMISSIONS_MAX_LENGTH)
            + ".'}",
        )

    def test_duplicate_permission_value(self):
        with self.assertRaises(XRPLModelException) as error:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(permission_value=TransactionType.ORACLE_DELETE),
                    Permission(permission_value=TransactionType.ORACLE_DELETE),
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
                    Permission(
                        permission_value=GranularPermission.MPTOKEN_ISSUANCE_LOCK
                    ),
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'account_addresses': 'Field `authorize` and `account` must be different."
            + "'}",
        )

    def test_non_delegable_transactions(self):
        with self.assertRaises(XRPLModelException) as error:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(
                        permission_value=GranularPermission.MPTOKEN_ISSUANCE_LOCK
                    ),
                    Permission(permission_value=TransactionType.ACCOUNT_DELETE),
                ],
            )
        self.assertEqual(
            error.exception.args[0],
            "{'permissions': \"Non-delegable transactions found in `permissions` "
            "list: {<TransactionType.ACCOUNT_DELETE: 'AccountDelete'>}.\"}",
        )

    def test_delegate_sponsorship_set_is_valid(self):
        """SponsorshipSet can be delegated at the transaction level."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
        )
        self.assertTrue(tx.is_valid())
        d = tx.to_dict()
        self.assertEqual(
            d["permissions"][0]["permission"]["permission_value"], "SponsorshipSet"
        )

    def test_delegate_sponsorship_set_to_xrpl_camel_case(self):
        """to_xrpl() emits CamelCase keys for a SponsorshipSet delegation."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
        )
        xrpl_dict = tx.to_xrpl()
        self.assertIn("Permissions", xrpl_dict)
        perm = xrpl_dict["Permissions"][0]
        self.assertEqual(perm["Permission"]["PermissionValue"], "SponsorshipSet")

    def test_delegate_sponsorship_set_roundtrip(self):
        """Roundtrip preserves the SponsorshipSet transaction-level permission."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
        )
        roundtripped = DelegateSet.from_dict(tx.to_dict())
        self.assertEqual(
            roundtripped.permissions[0].permission_value,
            TransactionType.SPONSORSHIP_SET,
        )

    def test_delegate_sponsorship_transfer_rejected(self):
        """SponsorshipTransfer is not delegable and must be rejected."""
        with self.assertRaises(XRPLModelException) as cm:
            DelegateSet(
                account=_ACCOUNT,
                authorize=_DELEGATED_ACCOUNT,
                permissions=[
                    Permission(permission_value=TransactionType.SPONSORSHIP_TRANSFER)
                ],
            )
        self.assertIn("Non-delegable", str(cm.exception))
