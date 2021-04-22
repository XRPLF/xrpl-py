from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, submit_transaction
from tests.integration.reusable_values import DESTINATION as DESTINATION_WALLET
from tests.integration.reusable_values import WALLET
from xrpl.account import get_next_valid_seq_number
from xrpl.clients import XRPLRequestFailureException
from xrpl.ledger import get_fee
from xrpl.models.exceptions import XRPLException
from xrpl.models.transactions import AccountDelete, AccountSet, EscrowFinish, Payment
from xrpl.transaction import (
    XRPLReliableSubmissionException,
    get_transaction_from_hash,
    safe_sign_and_autofill_transaction,
    safe_sign_transaction,
    send_reliable_submission,
)

ACCOUNT = WALLET.classic_address
DESTINATION = DESTINATION_WALLET.classic_address

CLEAR_FLAG = 3
DOMAIN = "6578616D706C652E636F6D".lower()
EMAIL_HASH = "10000000002000000000300000000012"
MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
SET_FLAG = 8
TRANSFER_RATE = 0
TICK_SIZE = 10
FEE = "6000000"
DESTINATION_TAG = 3
OFFER_SEQUENCE = 7
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
FULFILLMENT = "A0028000"
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"


class TestTransaction(TestCase):
    def test_reliable_submission_simple(self):
        WALLET.sequence = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        account_set = AccountSet(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            set_flag=SET_FLAG,
        )
        signed_account_set = safe_sign_and_autofill_transaction(
            account_set, WALLET, JSON_RPC_CLIENT
        )
        response = send_reliable_submission(signed_account_set, JSON_RPC_CLIENT)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["Fee"], get_fee(JSON_RPC_CLIENT))
        WALLET.sequence += 1

    def test_reliable_submission_payment(self):
        WALLET.sequence = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        payment_dict = {
            "account": ACCOUNT,
            "sequence": WALLET.sequence,
            "amount": "10",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        signed_payment_transaction = safe_sign_and_autofill_transaction(
            payment_transaction, WALLET, JSON_RPC_CLIENT
        )
        response = send_reliable_submission(signed_payment_transaction, JSON_RPC_CLIENT)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["Fee"], get_fee(JSON_RPC_CLIENT))
        WALLET.sequence += 1

    def test_reliable_submission_last_ledger_expiration(self):
        WALLET.sequence = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        payment_dict = {
            "account": ACCOUNT,
            "sequence": WALLET.sequence,
            "last_ledger_sequence": WALLET.sequence + 1,
            "fee": "10",
            "amount": "100",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        signed_payment_transaction = safe_sign_and_autofill_transaction(
            payment_transaction, WALLET, JSON_RPC_CLIENT
        )
        with self.assertRaises(XRPLReliableSubmissionException):
            send_reliable_submission(signed_payment_transaction, JSON_RPC_CLIENT)
        WALLET.sequence -= 1

    def test_reliable_submission_bad_transaction(self):
        WALLET.sequence = get_next_valid_seq_number(ACCOUNT, JSON_RPC_CLIENT)
        payment_dict = {
            "account": ACCOUNT,
            "last_ledger_sequence": WALLET.sequence + 20,
            "fee": "10",
            "amount": "100",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        signed_payment_transaction = safe_sign_transaction(payment_transaction, WALLET)
        with self.assertRaises(XRPLRequestFailureException):
            send_reliable_submission(signed_payment_transaction, JSON_RPC_CLIENT)
        WALLET.sequence -= 1

    def test_get_transaction_from_hash(self):
        # GIVEN a new transaction (payment)
        payment_transaction = Payment(
            account=WALLET.classic_address, amount="100", destination=DESTINATION
        )

        # WHEN we sign locally and autofill the transaction
        signed_payment_transaction = safe_sign_and_autofill_transaction(
            payment_transaction, WALLET, JSON_RPC_CLIENT
        )

        # AND submit the transaction
        response = send_reliable_submission(signed_payment_transaction, JSON_RPC_CLIENT)

        # THEN we expect to retrieve this transaction from its hash
        payment = get_transaction_from_hash(response.result["hash"], JSON_RPC_CLIENT)

        # AND we expect the result Account to be the same as the original payment Acct
        self.assertEqual(payment.result["Account"], ACCOUNT)
        # AND we expect the response to be successful (200)
        self.assertTrue(payment.is_successful())

        WALLET.sequence += 1

    def test_get_transaction_from_hash_with_binary(self):
        # GIVEN a new transaction (payment)
        payment_transaction = Payment(
            account=WALLET.classic_address, amount="100", destination=DESTINATION
        )

        # WHEN we sign locally and autofill the transaction
        signed_payment_transaction = safe_sign_and_autofill_transaction(
            payment_transaction, WALLET, JSON_RPC_CLIENT
        )

        # AND submit the transaction
        response = send_reliable_submission(signed_payment_transaction, JSON_RPC_CLIENT)
        payment_hash = response.result["hash"]

        # THEN we expect to retrieve this transaction from its hash with the
        # binary parameter set to true
        payment = get_transaction_from_hash(payment_hash, JSON_RPC_CLIENT, True)

        # AND we expect the result hash to be the same as the original payment hash
        self.assertEqual(payment.result["hash"], payment_hash)
        # AND we expect the response to be successful (200)
        self.assertTrue(payment.is_successful())

        WALLET.sequence += 1

    def test_get_transaction_from_hash_with_min_max_ledgers(self):
        # GIVEN a new transaction (payment)
        payment_transaction = Payment(
            account=WALLET.classic_address, amount="100", destination=DESTINATION
        )

        # WHEN we sign locally and autofill the transaction
        signed_payment_transaction = safe_sign_and_autofill_transaction(
            payment_transaction, WALLET, JSON_RPC_CLIENT
        )

        # AND submit the transaction
        response = send_reliable_submission(signed_payment_transaction, JSON_RPC_CLIENT)
        payment_hash = response.result["hash"]
        payment_ledger_index = response.result["ledger_index"]

        # THEN we expect to retrieve this transaction from its hash with
        # min_ledger and max_ledger parameters
        payment = get_transaction_from_hash(
            payment_hash,
            JSON_RPC_CLIENT,
            False,
            payment_ledger_index - 500,
            payment_ledger_index + 500,
        )

        # AND we expect the result Account to be the same as the original payment Acct
        self.assertEqual(payment.result["Account"], ACCOUNT)
        # AND we expect the response to be successful (200)
        self.assertTrue(payment.is_successful())

        WALLET.sequence += 1

    def test_high_fee_account_delete_unauthorized(self):
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # GIVEN a new AccountDelete transaction
            account_delete = AccountDelete(
                account=ACCOUNT,
                # WITH fee higher than 5 XRP
                fee=FEE,
                sequence=WALLET.sequence,
                destination=DESTINATION,
                destination_tag=DESTINATION_TAG,
            )
            submit_transaction(account_delete, WALLET)

    def test_high_fee_account_set_unauthorized(self):
        # GIVEN a new AccountSet transaction
        account_set = AccountSet(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            clear_flag=CLEAR_FLAG,
            domain=DOMAIN,
            email_hash=EMAIL_HASH,
            message_key=MESSAGE_KEY,
            transfer_rate=TRANSFER_RATE,
            tick_size=TICK_SIZE,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            submit_transaction(account_set, WALLET)

    def test_payment_high_fee_authorized(self):
        # GIVEN a new Payment transaction
        response = submit_transaction(
            Payment(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                amount="1",
                # WITH the fee higher than 2 XRP
                fee=FEE,
                destination=DESTINATION,
            ),
            WALLET,
            # WITHOUT checking the fee value
            check_fee=False,
        )
        # THEN we expect the transaction to be successful
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1

    def test_calculate_account_delete_fee(self):
        # GIVEN a new AccountDelete transaction
        account_delete = AccountDelete(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            destination=DESTINATION,
            destination_tag=DESTINATION_TAG,
        )

        # AFTER autofilling the transaction fee
        account_delete_signed = safe_sign_and_autofill_transaction(
            account_delete, WALLET, JSON_RPC_CLIENT
        )

        # THEN we expect the calculated fee to be 5000000 drops (5 XRP)
        expected_fee = "5000000"
        self.assertEqual(account_delete_signed.fee, expected_fee)

    def test_calculate_escrow_finish_fee(self):
        # GIVEN a new EscrowFinish transaction
        escrow_finish = EscrowFinish(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
            condition=CONDITION,
            fulfillment=FULFILLMENT,
        )

        # AFTER autofilling the transaction fee
        escrow_finish_signed = safe_sign_and_autofill_transaction(
            escrow_finish, WALLET, JSON_RPC_CLIENT
        )

        # AND calculating the expected fee with the formula
        # 10 drops × (33 + (Fulfillment size in bytes ÷ 16))
        net_fee = int(get_fee(JSON_RPC_CLIENT))
        fulfillment_in_bytes = FULFILLMENT.encode("ascii")
        expected_fee = net_fee * (33 + len(fulfillment_in_bytes) / 16)

        # THEN we expect the fee to be the calculation result above
        self.assertEqual(float(escrow_finish_signed.fee), float(expected_fee))

    def test_calculate_payment_fee(self):
        # GIVEN a new Payment transaction
        payment = Payment(
            account=WALLET.classic_address, amount="100", destination=DESTINATION
        )

        # AFTER autofilling the transaction fee
        payment_signed = safe_sign_and_autofill_transaction(
            payment, WALLET, JSON_RPC_CLIENT
        )

        # THEN We expect the fee to be the default network fee (usually 10 drops)
        expected_fee = get_fee(JSON_RPC_CLIENT)
        self.assertEqual(payment_signed.fee, expected_fee)
