import unittest

from xrpl.models.issued_currency import IssuedCurrency

currency = "BTC"
value = 100
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
issued_currency_dict = {
    "currency": currency,
    "value": value,
    "issuer": issuer,
}


class TestBaseModel(unittest.TestCase):
    def test_eq(self):
        issued_currency = IssuedCurrency(currency=currency, value=value, issuer=issuer)
        self.assertEqual(
            issued_currency, IssuedCurrency.from_dict(issued_currency_dict)
        )

    def test_repr(self):
        issued_currency = IssuedCurrency.from_dict(issued_currency_dict)
        expected_repr = (
            "IssuedCurrency(currency='BTC', value=100, "
            "issuer='r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ')"
        )
        self.assertEqual(repr(issued_currency), expected_repr)
