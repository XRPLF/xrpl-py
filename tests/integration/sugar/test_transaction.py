from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import FEE
from xrpl.models.transactions import Payment
from xrpl.transaction import (
    get_latest_transaction_from_account,
    send_reliable_submission,
)
from xrpl.wallet import Wallet, generate_faucet_wallet

NEW_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
EMPTY_WALLET = Wallet.generate_seed_and_wallet()


class TestTransaction(TestCase):
    def test_get_latest_transaction(self):
        # NOTE: this test may take a long time to run
        amount = "21000000"
        payment = Payment(
            account=NEW_WALLET.classic_address,
            destination=EMPTY_WALLET.classic_address,
            fee=FEE,
            sequence=NEW_WALLET.next_sequence_num,
            amount=amount,
            last_ledger_sequence=NEW_WALLET.next_sequence_num + 20,
        )
        send_reliable_submission(payment, NEW_WALLET, JSON_RPC_CLIENT)
        response = get_latest_transaction_from_account(
            NEW_WALLET.classic_address, JSON_RPC_CLIENT
        )
        self.assertEqual(len(response.result["transactions"]), 1)
        transaction = response.result["transactions"][0]["tx"]
        self.assertEqual(transaction["TransactionType"], "Payment")
        self.assertEqual(transaction["Amount"], amount)
        self.assertEqual(transaction["Account"], NEW_WALLET.classic_address)
