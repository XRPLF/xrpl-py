import unittest

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import CheckCreate

currency = "BTC"
value = "100"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
amount_dict = {
    "currency": currency,
    "issuer": issuer,
    "value": value,
}


class TestBaseModel(unittest.TestCase):
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
        account = issuer
        destination = issuer
        send_max = amount_dict
        check_create_dict = {
            "account": account,
            "destination": destination,
            "send_max": send_max,
        }
        check_create = CheckCreate.from_dict(check_create_dict)

        expected_dict = {
            **check_create_dict,
            "transaction_type": "CheckCreate",
            "flags": 0,
        }
        self.assertEqual(expected_dict, check_create.to_dict())
