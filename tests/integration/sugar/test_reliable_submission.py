from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import FEE
from tests.integration.reusable_values import WALLET as DESTINATION_WALLET
from xrpl.account import get_next_valid_seq_number
from xrpl.models.transactions import AccountSet, Payment
from xrpl.transaction import XRPLReliableSubmissionException, send_reliable_submission
from xrpl.wallet import generate_faucet_wallet

WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)

ACCOUNT = WALLET.classic_address
DESTINATION = DESTINATION_WALLET.classic_address

CLEAR_FLAG = 3
DOMAIN = "6578616D706C652E636F6D".lower()
EMAIL_HASH = "10000000002000000000300000000012"
MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
SET_FLAG = 8
TRANSFER_RATE = 0
TICK_SIZE = 10


class TestReliableSubmission(TestCase):
    def test_simple(self):
        WALLET.next_sequence_num = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        account_set = AccountSet(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
            set_flag=SET_FLAG,
            last_ledger_sequence=WALLET.next_sequence_num + 10,
        )
        response = send_reliable_submission(account_set, WALLET, JSON_RPC_CLIENT)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())

    def test_payment(self):
        WALLET.next_sequence_num = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        payment_dict = {
            "account": ACCOUNT,
            "sequence": WALLET.next_sequence_num,
            "last_ledger_sequence": WALLET.next_sequence_num + 10,
            "fee": "10000",
            "amount": "10",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        response = send_reliable_submission(
            payment_transaction, WALLET, JSON_RPC_CLIENT
        )
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())

    def test_last_ledger_expiration(self):
        WALLET.next_sequence_num = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        payment_dict = {
            "account": ACCOUNT,
            "sequence": WALLET.next_sequence_num,
            "last_ledger_sequence": WALLET.next_sequence_num + 1,
            "fee": "10000",
            "amount": "100",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        with self.assertRaises(XRPLReliableSubmissionException):
            send_reliable_submission(payment_transaction, WALLET, JSON_RPC_CLIENT)
