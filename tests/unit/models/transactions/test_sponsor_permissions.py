"""Tests for transaction-level delegation of sponsor transactions (XLS-68).

The former SponsorFee / SponsorReserve *granular* permissions were removed from
rippled (PR #7665). Sponsor delegation is now transaction-level: SponsorshipSet
is delegable, while SponsorshipTransfer is not.
"""

from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.delegate_set import DelegateSet, Permission
from xrpl.models.transactions.types import TransactionType

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_ACCOUNT2 = "rPyfep3gcLzkH4MYxKxJhE7bgUJfUCJM83"


class TestSponsorDelegation(TestCase):
    def test_delegate_sponsorship_set_is_valid(self):
        """SponsorshipSet can be delegated at the transaction level."""
        tx = DelegateSet(
            account=_ACCOUNT,
            authorize=_ACCOUNT2,
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
            authorize=_ACCOUNT2,
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
            authorize=_ACCOUNT2,
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
                authorize=_ACCOUNT2,
                permissions=[
                    Permission(permission_value=TransactionType.SPONSORSHIP_TRANSFER)
                ],
            )
        self.assertIn("Non-delegable", str(cm.exception))
