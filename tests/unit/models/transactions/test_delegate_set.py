from unittest import TestCase

from xrpl.core.binarycodec import decode, encode
from xrpl.core.binarycodec.definitions.definitions import (
    _DELEGABLE_PERMISSIONS_CODE_TO_STR_MAP,
    _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP,
)
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

    def test_non_delegable_vault_and_loan_transactions(self):
        # rippled marks all Vault (XLS-65) and Loan/LoanBroker transactions as
        # NotDelegable; each must be rejected in a DelegateSet permission list.
        non_delegable_types = [
            TransactionType.VAULT_CREATE,
            TransactionType.VAULT_SET,
            TransactionType.VAULT_DELETE,
            TransactionType.VAULT_DEPOSIT,
            TransactionType.VAULT_WITHDRAW,
            TransactionType.VAULT_CLAWBACK,
            TransactionType.LOAN_BROKER_SET,
            TransactionType.LOAN_BROKER_DELETE,
            TransactionType.LOAN_BROKER_COVER_DEPOSIT,
            TransactionType.LOAN_BROKER_COVER_WITHDRAW,
            TransactionType.LOAN_BROKER_COVER_CLAWBACK,
            TransactionType.LOAN_SET,
            TransactionType.LOAN_DELETE,
            TransactionType.LOAN_MANAGE,
            TransactionType.LOAN_PAY,
        ]
        for tx_type in non_delegable_types:
            with self.assertRaises(XRPLModelException):
                DelegateSet(
                    account=_ACCOUNT,
                    authorize=_DELEGATED_ACCOUNT,
                    permissions=[Permission(permission_value=tx_type)],
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

    def test_sponsorship_set_is_delegable_permission(self):
        """SponsorshipSet maps to a delegation code (tx-type code + 1)."""
        code = _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP["SponsorshipSet"]
        self.assertEqual(_DELEGABLE_PERMISSIONS_CODE_TO_STR_MAP[code], "SponsorshipSet")

    def test_removed_granular_sponsor_permissions_absent(self):
        """The old SponsorFee / SponsorReserve granular permissions are gone."""
        self.assertNotIn("SponsorFee", _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP)
        self.assertNotIn("SponsorReserve", _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP)

    def test_sponsorship_set_delegation_binary_roundtrip(self):
        """A SponsorshipSet delegation encodes/decodes via the binary codec."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_DELEGATED_ACCOUNT,
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
            sequence=1,
            fee="12",
        )
        decoded = decode(encode(tx.to_xrpl()))
        perm_value = decoded["Permissions"][0]["Permission"]["PermissionValue"]
        self.assertEqual(perm_value, "SponsorshipSet")

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
