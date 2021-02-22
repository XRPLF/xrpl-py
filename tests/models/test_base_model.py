import unittest

from xrpl.models.amount import IssuedCurrency

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
        amount = IssuedCurrency(**amount_dict)
        self.assertEqual(amount, IssuedCurrency(**amount_dict))

    def test_repr(self):
        amount = IssuedCurrency(**amount_dict)
        expected_repr = (
            "IssuedCurrency(currency='BTC', value='100', "
            "issuer='r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ')"
        )
        self.assertEqual(repr(amount), expected_repr)
