from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import DESTINATION, FEE, WALLET
from xrpl.account import (
    does_account_exist,
    get_account_transactions,
    get_balance,
    get_latest_transaction,
)
from xrpl.models.transactions import Payment
from xrpl.transaction import send_reliable_submission
from xrpl.wallet import Wallet, generate_faucet_wallet

NEW_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
EMPTY_WALLET = Wallet.create()


class TestAccount(TestCase):
    def test_does_account_exist_true(self):
        self.assertTrue(does_account_exist(WALLET.classic_address, JSON_RPC_CLIENT))

    def test_does_account_exist_false(self):
        address = "rG1QQv2nh2gr7RCZ1P8YYcBUcCCN633jCn"
        self.assertFalse(does_account_exist(address, JSON_RPC_CLIENT))

    def test_get_balance(self):
        self.assertEqual(
            get_balance(NEW_WALLET.classic_address, JSON_RPC_CLIENT), 1000000000
        )

    def test_get_account_transactions(self):
        transactions = get_account_transactions(
            NEW_WALLET.classic_address, JSON_RPC_CLIENT
        )
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["tx"]["TransactionType"], "Payment")
        self.assertEqual(transactions[0]["tx"]["Amount"], "1000000000")

    def test_get_account_transactions_empty(self):
        transactions = get_account_transactions(
            EMPTY_WALLET.classic_address, JSON_RPC_CLIENT
        )
        self.assertEqual(len(transactions), 0)

    def test_payment_transactions(self):
        transactions = get_account_transactions(
            NEW_WALLET.classic_address, JSON_RPC_CLIENT
        )
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["tx"]["TransactionType"], "Payment")
        self.assertEqual(transactions[0]["tx"]["Amount"], "1000000000")

    def test_get_latest_transaction(self):
        # NOTE: this test may take a long time to run
        amount = "21000000"
        payment = Payment(
            account=WALLET.classic_address,
            destination=DESTINATION.classic_address,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
            amount=amount,
            last_ledger_sequence=WALLET.next_sequence_num + 20,
        )
        send_reliable_submission(payment, WALLET, JSON_RPC_CLIENT)
        response = get_latest_transaction(WALLET.classic_address, JSON_RPC_CLIENT)
        self.assertEqual(len(response.result["transactions"]), 1)
        transaction = response.result["transactions"][0]["tx"]
        self.assertEqual(transaction["TransactionType"], "Payment")
        self.assertEqual(transaction["Amount"], amount)
        self.assertEqual(transaction["Account"], WALLET.classic_address)
