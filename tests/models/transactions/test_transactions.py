import unittest

from xrpl.models.transactions.offer_cancel_transaction import OfferCancelTransaction
from xrpl.models.transactions.offer_create_transaction import OfferCreateTransaction
from xrpl.models.transactions.set_regular_key_transaction import (
    SetRegularKeyTransaction,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestOfferCancelTransaction(unittest.TestCase):
    def test_init_to_json_object(self):
        offer_sequence = 29384723
        transaction = OfferCancelTransaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            offer_sequence=offer_sequence,
        )
        expected_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "offer_sequence": offer_sequence,
            "type": "OfferCancel",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        offer_sequence = 29384723
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "offer_sequence": offer_sequence,
            "sequence": _SEQUENCE,
        }
        transaction = OfferCancelTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "OfferCancel"}
        self.assertEqual(transaction.to_json_object(), expected_dict)


class TestOfferCreateTransaction(unittest.TestCase):
    def test_init_only_named(self):
        taker_gets = "3000000"
        taker_pays = "3000000"
        with self.assertRaises(TypeError):
            OfferCreateTransaction(
                _ACCOUNT,
                _FEE,
                _SEQUENCE,
                taker_gets,
                taker_pays,
            )

    def test_init_to_json_object(self):
        taker_gets = "3000000"
        taker_pays = "3000000"
        transaction = OfferCreateTransaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
        )
        expected_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "taker_gets": taker_gets,
            "taker_pays": taker_pays,
            "sequence": _SEQUENCE,
            "type": "OfferCreate",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        taker_gets = {
            "currency": "BTC",
            "value": 100,
            "issuer": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
        }
        taker_pays = "3000000"
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "taker_gets": taker_gets,
            "taker_pays": taker_pays,
            "sequence": _SEQUENCE,
        }
        transaction = OfferCreateTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "OfferCreate"}
        self.assertEqual(transaction.to_json_object(), expected_dict)


class TestSetRegularKeyTransaction(unittest.TestCase):
    def test_init_to_json_object(self):
        regular_key = "randomkeyasdoifjasidfs"
        transaction = SetRegularKeyTransaction(
            account=_ACCOUNT, fee=_FEE, sequence=_SEQUENCE, regular_key=regular_key
        )
        expected_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "regular_key": regular_key,
            "type": "SetRegularKey",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        regular_key = "randomkeyasdoifjasidfs"
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "regular_key": regular_key,
            "sequence": _SEQUENCE,
        }
        transaction = SetRegularKeyTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "SetRegularKey"}
        self.assertEqual(transaction.to_json_object(), expected_dict)
