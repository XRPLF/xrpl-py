import unittest

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.account_set_transaction import AccountSetTransaction
from xrpl.models.transactions.offer_cancel_transaction import OfferCancelTransaction
from xrpl.models.transactions.offer_create_transaction import OfferCreateTransaction


class TestAccountSetTransaction(unittest.TestCase):
    def test_init_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 29384723
        set_flag = 2
        transaction = AccountSetTransaction(
            account=account, fee=fee, sequence=sequence, set_flag=set_flag
        )
        expected_dict = {
            "account": account,
            "fee": fee,
            "sequence": sequence,
            "set_flag": set_flag,
            "type": "AccountSet",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 0
        set_flag = 7
        clear_flag = 3
        domain = "asjcsodafsaid0f9asdfasdf"
        transfer_rate = 1000000009
        tick_size = 8
        email_hash = "aosdijfaoisdf"
        message_key = "zoxicjvosidfas"
        transaction_dict = {
            "account": account,
            "fee": fee,
            "sequence": sequence,
            "clear_flag": clear_flag,
            "set_flag": set_flag,
            "domain": domain,
            "transfer_rate": transfer_rate,
            "tick_size": tick_size,
            "email_hash": email_hash,
            "message_key": message_key,
        }
        transaction = AccountSetTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "AccountSet"}
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_set_flag_and_clear_flag(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 0
        set_flag = 3
        clear_flag = 3
        domain = "asjcsodafsaid0f9asdfasdf"
        transaction_dict = {
            "account": account,
            "fee": fee,
            "set_flag": set_flag,
            "clear_flag": clear_flag,
            "domain": domain,
            "sequence": sequence,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_uppercase_domain(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 0
        clear_flag = 3
        domain = "asjcsodAOIJFsaid0f9asdfasdf"
        transaction_dict = {
            "account": account,
            "fee": fee,
            "clear_flag": clear_flag,
            "domain": domain,
            "sequence": sequence,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_invalid_tick_size(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 0
        clear_flag = 3
        tick_size = 39
        transaction_dict = {
            "account": account,
            "fee": fee,
            "clear_flag": clear_flag,
            "tick_size": tick_size,
            "sequence": sequence,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_invalid_transfer_rate(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 0
        clear_flag = 3
        transfer_rate = 39
        transaction_dict = {
            "account": account,
            "fee": fee,
            "clear_flag": clear_flag,
            "transfer_rate": transfer_rate,
            "sequence": sequence,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)


class TestOfferCreateTransaction(unittest.TestCase):
    def test_init_only_named(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        taker_gets = "3000000"
        taker_pays = "3000000"
        sequence = 0
        with self.assertRaises(TypeError):
            OfferCreateTransaction(
                account,
                fee,
                sequence,
                taker_gets,
                taker_pays,
            )

    def test_init_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        taker_gets = "3000000"
        taker_pays = "3000000"
        sequence = 0
        transaction = OfferCreateTransaction(
            account=account,
            fee=fee,
            sequence=sequence,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
        )
        expected_dict = {
            "account": account,
            "fee": fee,
            "taker_gets": taker_gets,
            "taker_pays": taker_pays,
            "sequence": sequence,
            "type": "OfferCreate",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        taker_gets = {
            "currency": "BTC",
            "value": 100,
            "issuer": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
        }
        taker_pays = "3000000"
        sequence = 0
        transaction_dict = {
            "account": account,
            "fee": fee,
            "taker_gets": taker_gets,
            "taker_pays": taker_pays,
            "sequence": sequence,
        }
        transaction = OfferCreateTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "OfferCreate"}
        self.assertEqual(transaction.to_json_object(), expected_dict)


class TestOfferCancelTransaction(unittest.TestCase):
    def test_init_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        offer_sequence = 29384723
        sequence = 0
        transaction = OfferCancelTransaction(
            account=account, fee=fee, sequence=sequence, offer_sequence=offer_sequence
        )
        expected_dict = {
            "account": account,
            "fee": fee,
            "sequence": sequence,
            "offer_sequence": offer_sequence,
            "type": "OfferCancel",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        offer_sequence = 29384723
        sequence = 0
        transaction_dict = {
            "account": account,
            "fee": fee,
            "offer_sequence": offer_sequence,
            "sequence": sequence,
        }
        transaction = OfferCancelTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "OfferCancel"}
        self.assertEqual(transaction.to_json_object(), expected_dict)
