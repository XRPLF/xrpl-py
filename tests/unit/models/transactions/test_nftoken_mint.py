from sys import maxsize
from unittest import TestCase

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import NFTokenMint

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_XRP_AMOUNT = "10000"
_XRP_INVALID_AMOUNT = "-1"
_ISSUED_CURRENCY_INVALID_AMOUNT = IssuedCurrencyAmount(
    currency="BTC", value="-1", issuer=_ACCOUNT
)
_ANOTHER_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_EXPIRATION = 1719820800


class TestNFTokenMint(TestCase):
    def test_issuer_is_account(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                issuer=_ACCOUNT,
            )

    def test_transfer_fee_too_high(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                transfer_fee=maxsize,
            )

    def test_uri_too_long(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                uri=_ACCOUNT * 1000,
            )

    def test_amount_native_negative(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                amount=_XRP_INVALID_AMOUNT,
            )

    def test_amount_issued_currency_negative(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                amount=_ISSUED_CURRENCY_INVALID_AMOUNT,
            )

    def test_destination_equals_account(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                amount=_XRP_AMOUNT,
                destination=_ACCOUNT,
            )

    def test_destination_without_amount(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                destination=_ANOTHER_ACCOUNT,
            )

    def test_expiration_without_amount(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                expiration=_EXPIRATION,
            )
