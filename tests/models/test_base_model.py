import unittest

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests.book_offers import BookOffers
from xrpl.models.requests.sign import Sign
from xrpl.models.transactions import CheckCreate

currency = "BTC"
value = "100"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
amount_dict = {
    "currency": currency,
    "issuer": issuer,
    "value": value,
}

account = issuer
destination = issuer
send_max = amount_dict
check_create_dict = {
    "account": account,
    "destination": destination,
    "send_max": send_max,
}

secret = "topsecretpassword"


class TestBaseModel(unittest.TestCase):
    maxDiff = 1000

    def test_eq(self):
        amount = IssuedCurrencyAmount(**amount_dict)
        self.assertEqual(amount, IssuedCurrencyAmount(**amount_dict))

    def test_repr(self):
        amount = IssuedCurrencyAmount(**amount_dict)
        expected_repr = (
            f"IssuedCurrencyAmount(currency='{currency}', "
            f"issuer='{issuer}', value='{value}')"
        )
        self.assertEqual(repr(amount), expected_repr)

    def test_from_dict_basic(self):
        amount = IssuedCurrencyAmount.from_dict(amount_dict)
        self.assertEqual(amount, IssuedCurrencyAmount(**amount_dict))

    def test_from_dict_recursive_amount(self):
        check_create = CheckCreate.from_dict(check_create_dict)

        expected_dict = {
            **check_create_dict,
            "transaction_type": "CheckCreate",
            "flags": 0,
        }
        self.assertEqual(expected_dict, check_create.to_dict())

    def test_from_dict_recursive_currency(self):
        xrp = {"currency": "XRP"}
        issued_currency = {
            "currency": currency,
            "issuer": issuer,
        }
        book_offers_dict = {
            "taker_gets": xrp,
            "taker_pays": issued_currency,
        }
        book_offers = BookOffers.from_dict(book_offers_dict)

        expected_dict = {
            **book_offers_dict,
            "method": "book_offers",
            "taker_gets": {"currency": "XRP"},
        }
        self.assertEqual(expected_dict, book_offers.to_dict())

    def test_from_dict_recursive_transaction(self):
        transaction = CheckCreate.from_dict(check_create_dict)
        sign_dict = {"secret": secret, "transaction": transaction.to_dict()}
        sign = Sign.from_dict(sign_dict)

        expected_dict = {
            **sign_dict,
            "tx_json": transaction.to_dict(),
            "method": "sign",
            "fee_mult_max": 10,
            "fee_div_max": 1,
            "offline": False,
        }
        del expected_dict["transaction"]
        self.assertEqual(expected_dict, sign.to_dict())

    def test_from_dict_recursive_transaction_tx_json(self):
        transaction = CheckCreate.from_dict(check_create_dict)
        sign_dict = {"secret": secret, "tx_json": transaction.to_dict()}
        sign = Sign.from_dict(sign_dict)

        expected_dict = {
            **sign_dict,
            "tx_json": transaction.to_dict(),
            "method": "sign",
            "fee_mult_max": 10,
            "fee_div_max": 1,
            "offline": False,
        }
        self.assertEqual(expected_dict, sign.to_dict())
