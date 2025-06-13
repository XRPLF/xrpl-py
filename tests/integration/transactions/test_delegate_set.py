from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.requests import AccountObjects, AccountObjectType, LedgerEntry
from xrpl.models.requests.ledger_entry import Delegate
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import (
    AccountSet,
    DelegateSet,
    GranularPermission,
    Payment,
)
from xrpl.models.transactions.delegate_set import Permission
from xrpl.models.transactions.types import TransactionType
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

        # Sending a transaction without a delegate permission results in
        # tecNO_DELEGATE_PERMISSION
        self.assertEqual(response.result["engine_result"], "tecNO_DELEGATE_PERMISSION")

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
            # Authorize bob account to execute Payment transactions and
            # modify the domain of an account behalf of alice's account.
            permissions=[
                Permission(permission_value=TransactionType.PAYMENT),
                Permission(permission_value=GranularPermission.ACCOUNT_DOMAIN_SET),
            ],
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

        # Use the bob's account to execute a transaction on behalf of alice
        account_set = AccountSet(
            account=alice.address,
            delegate=bob.address,
            email_hash="10000000002000000000300000000012",
        )
        response = await sign_and_reliable_submission_async(
            account_set, bob, client, check_fee=False
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_DELEGATE_PERMISSION")

        # test ledger entry
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
        self.assertEqual(len(ledger_entry_response.result["node"]["Permissions"]), 2)

    @test_async_and_sync(globals())
    async def test_fetch_delegate_account_objects(self, client):
        # Note: Using WALLET, DESTINATION accounts could pollute the test results
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        delegate_set = DelegateSet(
            account=alice.address,
            authorize=bob.address,
            # Authorize bob's account to execute Payment transactions
            # and authorize a trustline on behalf of alice's account.
            permissions=[
                Permission(permission_value=TransactionType.PAYMENT),
                Permission(permission_value=GranularPermission.TRUSTLINE_AUTHORIZE),
            ],
        )
        response = await sign_and_reliable_submission_async(
            delegate_set, alice, client, check_fee=False
        )

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(account=alice.address, type=AccountObjectType.DELEGATE)
        )

        granted_permission = {
            obj["Permission"]["PermissionValue"]
            for obj in account_objects_response.result["account_objects"][0][
                "Permissions"
            ]
        }

        self.assertEqual(len(granted_permission), 2)
        self.assertTrue(TransactionType.PAYMENT.value in granted_permission)
        self.assertTrue(
            GranularPermission.TRUSTLINE_AUTHORIZE.value in granted_permission
        )
