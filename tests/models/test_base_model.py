import unittest

from xrpl.models.amount import IssuedCurrencyAmount

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
        self.assertEqual(amount, IssuedCurrencyAmount.from_dict(amount_dict))

    def test_repr(self):
        amount = IssuedCurrencyAmount.from_dict(amount_dict)
        expected_repr = (
            "IssuedCurrencyAmount(currency='BTC', value='100', "
            "issuer='r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ')"
        )
        self.assertEqual(repr(amount), expected_repr)
