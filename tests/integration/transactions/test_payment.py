from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.amounts.mpt_amount import MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.transactions import Payment
from xrpl.models.transactions.mptoken_issuance_create import MPTokenIssuanceCreate


class TestPayment(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        response = await sign_and_reliable_submission_async(
            Payment(
                account=WALLET.address,
                amount="1",
                destination=DESTINATION.address,
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals())
    async def test_deliver_max_alias_field(self, client):
        delivered_amount = "200000"

        # Case-1: Only Amount field is present in the Payment transaction
        payment_tx_json = {
            "Account": "rGWTUVmm1fB5QUjMYn8KfnyrFNgDiD9H9e",
            "Destination": "rw71Qs1UYQrSQ9hSgRohqNNQcyjCCfffkQ",
            "TransactionType": "Payment",
            "Amount": delivered_amount,
            "Fee": "15",
            "Flags": 0,
            "Sequence": 144,
            "LastLedgerSequence": 6220218,
        }

        payment_txn = Payment.from_xrpl(payment_tx_json)
        self.assertEqual(delivered_amount, payment_txn.to_dict()["amount"])

        response = await sign_and_reliable_submission_async(
            payment_txn,
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())

        # Case-2: Only deliver_max field is present in the Payment transaction
        payment_tx_json = {
            "Account": "rGWTUVmm1fB5QUjMYn8KfnyrFNgDiD9H9e",
            "Destination": "rw71Qs1UYQrSQ9hSgRohqNNQcyjCCfffkQ",
            "TransactionType": "Payment",
            "DeliverMax": delivered_amount,
            "Fee": "15",
            "Flags": 0,
            "Sequence": 144,
            "LastLedgerSequence": 6220218,
        }

        payment_txn = Payment.from_xrpl(payment_tx_json)
        self.assertEqual(delivered_amount, payment_txn.to_dict()["amount"])

        response = await sign_and_reliable_submission_async(
            payment_txn,
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())

        # Case-3a: Both fields are present, with identical values
        payment_tx_json = {
            "Account": "rGWTUVmm1fB5QUjMYn8KfnyrFNgDiD9H9e",
            "Destination": "rw71Qs1UYQrSQ9hSgRohqNNQcyjCCfffkQ",
            "TransactionType": "Payment",
            "DeliverMax": delivered_amount,
            "Amount": delivered_amount,
            "Fee": "15",
            "Flags": 0,
            "Sequence": 144,
            "LastLedgerSequence": 6220218,
        }

        payment_txn = Payment.from_xrpl(payment_tx_json)
        self.assertEqual(delivered_amount, payment_txn.to_dict()["amount"])

        response = await sign_and_reliable_submission_async(
            payment_txn,
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())

        # Case-3b: Both fields are present, with different values
        payment_tx_json = {
            "Account": "rGWTUVmm1fB5QUjMYn8KfnyrFNgDiD9H9e",
            "Destination": "rw71Qs1UYQrSQ9hSgRohqNNQcyjCCfffkQ",
            "TransactionType": "Payment",
            "DeliverMax": delivered_amount,
            "Amount": "10",
            "Fee": "15",
            "Flags": 0,
            "Sequence": 144,
            "LastLedgerSequence": 6220218,
        }

        with self.assertRaises(XRPLModelException):
            payment_txn = Payment.from_xrpl(payment_tx_json)
            response = await sign_and_reliable_submission_async(
                payment_txn,
                WALLET,
                client,
            )
            self.assertFalse(response.is_successful())

        # Case-4: Both fields are absent in the Payment transaction
        payment_tx_json = {
            "Account": "rGWTUVmm1fB5QUjMYn8KfnyrFNgDiD9H9e",
            "Destination": "rw71Qs1UYQrSQ9hSgRohqNNQcyjCCfffkQ",
            "TransactionType": "Payment",
            "Fee": "15",
            "Flags": 0,
            "Sequence": 144,
            "LastLedgerSequence": 6220218,
        }

        with self.assertRaises(XRPLModelException):
            payment_txn = Payment.from_xrpl(payment_tx_json)
            response = await sign_and_reliable_submission_async(
                payment_txn,
                WALLET,
                client,
            )
            self.assertFalse(response.is_successful())

    @test_async_and_sync(globals())
    async def test_mpt_payment(self, client):
        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            maximum_amount="9223372036854775807",  # "7fffffffffffffff"
            asset_scale=2,
        )

        response = await sign_and_reliable_submission_async(
            tx,
            WALLET,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm MPTokenIssuance ledger object was created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        # subsequent integration tests (sync/async + json/websocket) add one
        # MPTokenIssuance object to the account
        account_objects = account_objects_response.result["account_objects"]
        self.assertTrue(len(account_objects) > 0)

        mpt_issuance_id = account_objects[0]["mpt_issuance_id"]

        payment = Payment(
            account=WALLET.address,
            amount=MPTAmount(mpt_issuance_id=mpt_issuance_id, value="10"),
            destination=DESTINATION.address,
        )

        response = await sign_and_reliable_submission_async(
            payment,
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
