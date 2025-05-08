from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.requests import LedgerEntry
from xrpl.models.requests.ledger_entry import Delegate
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DelegatableTransaction, DelegateSet, Payment
from xrpl.models.transactions.delegate_set import Permission
from xrpl.utils import xrp_to_drops
from xrpl.wallet.main import Wallet


class TestDelegateSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_delegation_with_no_permission(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)
        carol = Wallet.create()
        await fund_wallet_async(carol)

        # Use bob's account to execute a transaction on behalf of alice
        payment = Payment(
            account=alice.address,
            amount=xrp_to_drops(1),
            destination=carol.address,
            delegate=bob.address,
        )
        response = await sign_and_reliable_submission_async(
            payment, bob, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

        # The lack of AccountPermissionSet transaction will result in a tecNO_PERMISSION
        self.assertEqual(response.result["engine_result"], "tecNO_PERMISSION")

    @test_async_and_sync(globals())
    async def test_delegate_set_workflow(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)
        carol = Wallet.create()
        await fund_wallet_async(carol)

        delegate_set = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            # Authorize bob account to execute Payment transactions on
            # behalf of alice's account.
            # Note: Payment transaction has a TransactionType of 0
            permissions=[Permission(permission_value=DelegatableTransaction.PAYMENT)],
        )
        response = await sign_and_reliable_submission_async(
            delegate_set, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Use the bob's account to execute a transaction on behalf of alice
        payment = Payment(
            account=alice.address,
            amount=xrp_to_drops(1),
            destination=carol.address,
            delegate=bob.address,
        )
        response = await sign_and_reliable_submission_async(
            payment, bob, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Validate that the transaction was signed by bob
        self.assertEqual(response.result["tx_json"]["Account"], alice.address)
        self.assertEqual(response.result["tx_json"]["Delegate"], bob.address)
        self.assertEqual(response.result["tx_json"]["SigningPubKey"], bob.public_key)

    @test_async_and_sync(globals())
    async def test_fetch_delegate_ledger_entry(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        delegate_set = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            # Authorize bob's account to execute Payment transactions on
            # behalf of alice's account.
            # Note: Payment transaction has a TransactionType of 0
            permissions=[Permission(permission_value=DelegatableTransaction.PAYMENT)],
        )
        response = await sign_and_reliable_submission_async(
            delegate_set, alice, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        ledger_entry_response = await client.request(
            LedgerEntry(
                delegate=Delegate(
                    account=alice.address,
                    authorize=bob.address,
                ),
            )
        )
        self.assertTrue(ledger_entry_response.is_successful())
        self.assertEqual(
            ledger_entry_response.result["node"]["LedgerEntryType"],
            "Delegate",
        )
        self.assertEqual(ledger_entry_response.result["node"]["Account"], alice.address)
        self.assertEqual(ledger_entry_response.result["node"]["Authorize"], bob.address)
        self.assertEqual(len(ledger_entry_response.result["node"]["Permissions"]), 1)
