from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.requests import AccountInfo, LedgerEntry
from xrpl.models.requests.ledger_entry import AccountPermission
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountPermissionSet, Payment
from xrpl.models.transactions.account_permission_set import Permission
from xrpl.utils import xrp_to_drops
from xrpl.wallet.main import Wallet


class TestAccountPermissionSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_delegation_with_no_permission(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)
        carol = Wallet.create()
        await fund_wallet_async(carol)

        # Fetch the Sequence number of alice's account
        alice_account_info_response = await client.request(
            AccountInfo(
                account=alice.address,
            )
        )
        self.assertTrue(alice_account_info_response.is_successful())

        # Use bob's account to execute a transaction on behalf of alice
        payment = Payment(
            account=bob.address,
            amount=xrp_to_drops(1),
            destination=carol.address,
            on_behalf_of=alice.address,
            delegating_seq=int(
                alice_account_info_response.result["account_data"]["Sequence"]
            ),
        )
        response = await sign_and_reliable_submission_async(
            payment, bob, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

        # The lack of AccountPermissionSet transaction will result in a tecNO_PERMISSION
        self.assertEqual(response.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_account_permission_set_workflow(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)
        carol = Wallet.create()
        await fund_wallet_async(carol)

        account_permission_set = AccountPermissionSet(
            account=alice.address,
            authorize=bob.address,
            # Authorize bob account to execute Payment transactions on
            # behalf of alice's account.
            # Note: Payment transaction has a TransactionType of 0
            permissions=[Permission(permission_value=(1 + 0))],
        )
        response = await sign_and_reliable_submission_async(
            account_permission_set, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Fetch the Sequence number of the WALLET account
        alice_account_info_response = await client.request(
            AccountInfo(
                account=alice.address,
            )
        )
        self.assertTrue(alice_account_info_response.is_successful())

        # Use the bob's account to execute a transaction on behalf of alice
        payment = Payment(
            account=bob.address,
            amount=xrp_to_drops(1),
            destination=carol.address,
            on_behalf_of=alice.address,
            delegating_seq=int(
                alice_account_info_response.result["account_data"]["Sequence"]
            ),
        )
        response = await sign_and_reliable_submission_async(
            payment, bob, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_fetch_account_permission_ledger_entry(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        account_permission_set = AccountPermissionSet(
            account=alice.address,
            authorize=bob.address,
            # Authorize bob's account to execute Payment transactions on
            # behalf of alice's account.
            # Note: Payment transaction has a TransactionType of 0
            permissions=[Permission(permission_value=(1 + 0))],
        )
        response = await sign_and_reliable_submission_async(
            account_permission_set, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        ledger_entry_response = await client.request(
            LedgerEntry(
                account_permission=AccountPermission(
                    account=alice.address,
                    authorize=bob.address,
                ),
            )
        )
        self.assertTrue(ledger_entry_response.is_successful())
        self.assertEqual(
            ledger_entry_response.result["node"]["LedgerEntryType"],
            "AccountPermission",
        )
        self.assertEqual(ledger_entry_response.result["node"]["Account"], alice.address)
        self.assertEqual(ledger_entry_response.result["node"]["Authorize"], bob.address)
        self.assertEqual(len(ledger_entry_response.result["node"]["Permissions"]), 1)
