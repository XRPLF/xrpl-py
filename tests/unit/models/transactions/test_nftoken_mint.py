from sys import maxsize
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import NFTokenMint

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ANOTHER_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_FEE = "0.00001"
_SEQUENCE = 19048


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

    def test_nftoken_mint_sell_offer_with_zero_amount(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                amount="0",
            )

    def test_destination_is_account(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                destination=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                amount="1",
            )

    def test_nftoken_mint_sell_offer_with_negative_amount(self):
        with self.assertRaises(XRPLModelException):
            NFTokenMint(
                account=_ACCOUNT,
                destination=_ANOTHER_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_taxon=0,
                amount="-1",
            )
