"""Integration tests for transaction-level sponsor delegation.

Sponsor delegation is transaction-level: SponsorshipSet
is delegable (its delegation permission code is its transaction-type code + 1),
while SponsorshipTransfer is not delegable.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.core.binarycodec import decode, encode
from xrpl.core.binarycodec.definitions.definitions import (
    _DELEGABLE_PERMISSIONS_CODE_TO_STR_MAP,
    _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP,
)
from xrpl.models.requests import AccountObjects, AccountObjectType, LedgerEntry
from xrpl.models.requests.ledger_entry import Delegate
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DelegateSet
from xrpl.models.transactions.delegate_set import Permission
from xrpl.models.transactions.types import TransactionType
from xrpl.wallet.main import Wallet


class TestSponsorDelegation(IntegrationTestCase):
    # ------------------------------------------------------------------ #
    #  Codec-level (no network)                                           #
    # ------------------------------------------------------------------ #

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
            account="r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
            authorize="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
            sequence=1,
            fee="12",
        )
        decoded = decode(encode(tx.to_xrpl()))
        perm_value = decoded["Permissions"][0]["Permission"]["PermissionValue"]
        self.assertEqual(perm_value, "SponsorshipSet")

    # ------------------------------------------------------------------ #
    #  Network — transaction-level SponsorshipSet delegation accepted     #
    # ------------------------------------------------------------------ #

    @test_async_and_sync(globals())
    async def test_delegate_sponsorship_set_accepted(self, client):
        """DelegateSet delegating SponsorshipSet is accepted by rippled."""
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        tx = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
        )
        response = await sign_and_reliable_submission_async(
            tx, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        ledger_response = await client.request(
            LedgerEntry(delegate=Delegate(account=alice.address, authorize=bob.address))
        )
        self.assertTrue(ledger_response.is_successful())
        perm_values = {
            p["Permission"]["PermissionValue"]
            for p in ledger_response.result["node"]["Permissions"]
        }
        self.assertIn(TransactionType.SPONSORSHIP_SET.value, perm_values)

    @test_async_and_sync(globals())
    async def test_account_objects_sponsorship_set_delegation(self, client):
        """AccountObjects returns the delegated SponsorshipSet permission."""
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        tx = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            permissions=[Permission(permission_value=TransactionType.SPONSORSHIP_SET)],
        )
        response = await sign_and_reliable_submission_async(
            tx, alice, client, check_fee=False
        )
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        objects_response = await client.request(
            AccountObjects(account=alice.address, type=AccountObjectType.DELEGATE)
        )
        self.assertTrue(objects_response.is_successful())
        perm_values = {
            p["Permission"]["PermissionValue"]
            for p in objects_response.result["account_objects"][0]["Permissions"]
        }
        self.assertIn(TransactionType.SPONSORSHIP_SET.value, perm_values)
