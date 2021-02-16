import unittest

from xrpl.models.transactions.offer_cancel_transaction import OfferCancelTransaction
from xrpl.models.transactions.offer_create_transaction import OfferCreateTransaction
from xrpl.models.transactions.set_regular_key_transaction import (
    SetRegularKeyTransaction,
)


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


class TestSetRegularKeyTransaction(unittest.TestCase):
    def test_init_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 29384723
        regular_key = "randomkeyasdoifjasidfs"
        transaction = SetRegularKeyTransaction(
            account=account, fee=fee, sequence=sequence, regular_key=regular_key
        )
        expected_dict = {
            "account": account,
            "fee": fee,
            "sequence": sequence,
            "regular_key": regular_key,
            "type": "SetRegularKey",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        regular_key = "randomkeyasdoifjasidfs"
        sequence = 0
        transaction_dict = {
            "account": account,
            "fee": fee,
            "regular_key": regular_key,
            "sequence": sequence,
        }
        transaction = SetRegularKeyTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "SetRegularKey"}
        self.assertEqual(transaction.to_json_object(), expected_dict)
