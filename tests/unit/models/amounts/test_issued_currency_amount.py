from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies import XRP, IssuedCurrency

_ISSUER = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestIssuedCurrencyAmount(TestCase):
    def test_from_issued_currency(self):
        currency = "USD"
        amount = "12"
        issued_currency = IssuedCurrency(currency=currency, issuer=_ISSUER)
        issued_currency_amount = IssuedCurrencyAmount.from_issued_currency(
            issued_currency, amount
        )

        self.assertEqual(issued_currency_amount.currency, currency)
        self.assertEqual(issued_currency_amount.issuer, _ISSUER)
        self.assertEqual(issued_currency_amount.value, amount)

    def test_from_issued_currency_xrp(self):
        amount = "12"
        issued_currency_amount = IssuedCurrencyAmount.from_issued_currency(
            XRP(), amount
        )

        self.assertEqual(issued_currency_amount, amount)

    def test_get_issued_currency(self):
        currency = "USD"
        amount = "12"
        expected = IssuedCurrency(currency=currency, issuer=_ISSUER)

        issued_currency_amount = IssuedCurrencyAmount(
            currency=currency, issuer=_ISSUER, value=amount
        )
        result = issued_currency_amount.get_issued_currency()

        self.assertEqual(result, expected)
