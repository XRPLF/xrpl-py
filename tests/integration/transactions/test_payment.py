from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import Payment


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
