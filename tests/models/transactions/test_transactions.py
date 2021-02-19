import unittest

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions.account_delete_transaction import AccountDeleteTransaction
from xrpl.models.transactions.account_set_transaction import AccountSetTransaction
from xrpl.models.transactions.offer_cancel_transaction import OfferCancelTransaction
from xrpl.models.transactions.offer_create import OfferCreate
from xrpl.models.transactions.set_regular_key_transaction import (
    SetRegularKeyTransaction,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestAccountDeleteTransaction(unittest.TestCase):
    def test_init_to_json_object(self):
        transaction = AccountDeleteTransaction(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            destination=_ACCOUNT,
        )
        expected_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "destination": _ACCOUNT,
            "type": "AccountDelete",
        }
        self.assertEqual(transaction.to_json_object(), expected_dict)

    def test_from_dict_to_json_object(self):
        destination_tag = 20394
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "destination": _ACCOUNT,
            "destination_tag": destination_tag,
            "sequence": _SEQUENCE,
        }
        transaction = AccountDeleteTransaction.from_dict(transaction_dict)
        expected_dict = {**transaction_dict, "type": "AccountDelete"}
        self.assertEqual(transaction.to_json_object(), expected_dict)


class TestAccountSetTransaction(unittest.TestCase):
    def test_set_flag_and_clear_flag(self):
        set_flag = 3
        clear_flag = 3
        domain = "asjcsodafsaid0f9asdfasdf"
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "set_flag": set_flag,
            "clear_flag": clear_flag,
            "domain": domain,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_uppercase_domain(self):
        clear_flag = 3
        domain = "asjcsodAOIJFsaid0f9asdfasdf"
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "clear_flag": clear_flag,
            "domain": domain,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_invalid_tick_size(self):
        clear_flag = 3
        tick_size = 39
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "clear_flag": clear_flag,
            "tick_size": tick_size,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)

    def test_invalid_transfer_rate(self):
        clear_flag = 3
        transfer_rate = 39
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "clear_flag": clear_flag,
            "transfer_rate": transfer_rate,
            "sequence": _SEQUENCE,
        }
        with self.assertRaises(XRPLModelValidationException):
            AccountSetTransaction.from_dict(transaction_dict)
<<<<<<< HEAD


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


class TestOfferCreate(unittest.TestCase):
    def test_init_to_json_object(self):
        taker_gets = "3000000"
        taker_pays = "3000000"
        transaction = OfferCreate(
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
