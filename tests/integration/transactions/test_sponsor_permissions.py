"""Integration tests verifying SponsorFee/SponsorReserve wire values (65549/65550)."""

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
from xrpl.models.transactions.delegate_set import GranularPermission, Permission
from xrpl.wallet.main import Wallet

_SPONSOR_FEE_WIRE = 65549
_SPONSOR_RESERVE_WIRE = 65550


class TestSponsorPermissionsWireValues(IntegrationTestCase):
    # ------------------------------------------------------------------ #
    #  Codec-level (no network) — verify 65549 / 65550 round-trip        #
    # ------------------------------------------------------------------ #

    def test_sponsor_fee_wire_value_in_definitions(self):
        """SponsorFee must map to numeric wire value 65549."""
        self.assertEqual(
            _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP["SponsorFee"],
            _SPONSOR_FEE_WIRE,
        )

    def test_sponsor_reserve_wire_value_in_definitions(self):
        """SponsorReserve must map to numeric wire value 65550."""
        self.assertEqual(
            _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP["SponsorReserve"],
            _SPONSOR_RESERVE_WIRE,
        )

    def test_sponsor_fee_reverse_lookup(self):
        """Numeric code 65549 must decode back to 'SponsorFee'."""
        self.assertEqual(
            _DELEGABLE_PERMISSIONS_CODE_TO_STR_MAP[_SPONSOR_FEE_WIRE],
            "SponsorFee",
        )

    def test_sponsor_reserve_reverse_lookup(self):
        """Numeric code 65550 must decode back to 'SponsorReserve'."""
        self.assertEqual(
            _DELEGABLE_PERMISSIONS_CODE_TO_STR_MAP[_SPONSOR_RESERVE_WIRE],
            "SponsorReserve",
        )

    def test_sponsor_fee_binary_codec_roundtrip(self):
        """SponsorFee encodes to binary and decodes back via the codec."""
        tx = DelegateSet(
            account="r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
            authorize="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            permissions=[Permission(permission_value=GranularPermission.SPONSOR_FEE)],
            sequence=1,
            fee="12",
        )
        decoded = decode(encode(tx.to_xrpl()))
        perm_value = decoded["Permissions"][0]["Permission"]["PermissionValue"]
        self.assertEqual(perm_value, "SponsorFee")

    def test_sponsor_reserve_binary_codec_roundtrip(self):
        """SponsorReserve encodes to binary and decodes back via the codec."""
        tx = DelegateSet(
            account="r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
            authorize="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE)
            ],
            sequence=1,
            fee="12",
        )
        decoded = decode(encode(tx.to_xrpl()))
        perm_value = decoded["Permissions"][0]["Permission"]["PermissionValue"]
        self.assertEqual(perm_value, "SponsorReserve")

    def test_both_sponsor_permissions_binary_codec_roundtrip(self):
        """Both sponsor permissions encode/decode with correct wire values."""
        tx = DelegateSet(
            account="r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
            authorize="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
            ],
            sequence=1,
            fee="12",
        )
        decoded = decode(encode(tx.to_xrpl()))
        perm_values = {
            p["Permission"]["PermissionValue"] for p in decoded["Permissions"]
        }
        self.assertIn("SponsorFee", perm_values)
        self.assertIn("SponsorReserve", perm_values)

    def test_sponsor_fee_enum_value_matches_wire(self):
        """GranularPermission.SPONSOR_FEE string value maps to wire code 65549."""
        self.assertEqual(
            _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP[GranularPermission.SPONSOR_FEE],
            _SPONSOR_FEE_WIRE,
        )

    def test_sponsor_reserve_enum_value_matches_wire(self):
        """GranularPermission.SPONSOR_RESERVE string value maps to wire code 65550."""
        self.assertEqual(
            _DELEGABLE_PERMISSIONS_STR_TO_CODE_MAP[GranularPermission.SPONSOR_RESERVE],
            _SPONSOR_RESERVE_WIRE,
        )

    # ------------------------------------------------------------------ #
    #  Network — DelegateSet with sponsor permissions accepted by rippled #
    # ------------------------------------------------------------------ #

    @test_async_and_sync(globals())
    async def test_delegate_set_sponsor_fee_accepted(self, client):
        """DelegateSet with SponsorFee is accepted by rippled (wire value correct)."""
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        tx = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            permissions=[Permission(permission_value=GranularPermission.SPONSOR_FEE)],
        )
        response = await sign_and_reliable_submission_async(
            tx, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_delegate_set_sponsor_reserve_accepted(self, client):
        """DelegateSet with SponsorReserve is accepted by rippled (wire value correct)."""
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        tx = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE)
            ],
        )
        response = await sign_and_reliable_submission_async(
            tx, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_ledger_returns_sponsor_permission_values(self, client):
        """Ledger entry round-trips SponsorFee and SponsorReserve string names."""
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        tx = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
            ],
        )
        response = await sign_and_reliable_submission_async(
            tx, alice, client, check_fee=False
        )
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        ledger_response = await client.request(
            LedgerEntry(
                delegate=Delegate(account=alice.address, authorize=bob.address)
            )
        )
        self.assertTrue(ledger_response.is_successful())

        perm_values = {
            p["Permission"]["PermissionValue"]
            for p in ledger_response.result["node"]["Permissions"]
        }
        self.assertIn(GranularPermission.SPONSOR_FEE.value, perm_values)
        self.assertIn(GranularPermission.SPONSOR_RESERVE.value, perm_values)

    @test_async_and_sync(globals())
    async def test_account_objects_sponsor_permissions(self, client):
        """AccountObjects returns SponsorFee and SponsorReserve permission values."""
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        tx = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            permissions=[
                Permission(permission_value=GranularPermission.SPONSOR_FEE),
                Permission(permission_value=GranularPermission.SPONSOR_RESERVE),
            ],
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
        self.assertIn(GranularPermission.SPONSOR_FEE.value, perm_values)
        self.assertIn(GranularPermission.SPONSOR_RESERVE.value, perm_values)
