from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies import IssuedCurrency

_ISSUER = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestIssuedCurrencyAmount(TestCase):
    def test_to_currency(self):
        currency = "USD"
        amount = "12"
        expected = IssuedCurrency(currency=currency, issuer=_ISSUER)

        issued_currency_amount = IssuedCurrencyAmount(
            currency=currency, issuer=_ISSUER, value=amount
        )
        result = issued_currency_amount.to_currency()

        self.assertEqual(result, expected)
