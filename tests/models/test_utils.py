import unittest

from xrpl.models.currencies import IssuedCurrency

currency = "BTC"
value = "100"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
currency_dict = {
    "currency": currency,
    "issuer": issuer,
    "value": value,
}


class TestUtils(unittest.TestCase):
    def test_kwargs_req(self):
        with self.assertRaises(TypeError):
            IssuedCurrency(currency, issuer)
