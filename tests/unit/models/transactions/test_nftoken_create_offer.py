from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import NFTokenCreateOffer, NFTokenCreateOfferFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ANOTHER_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_FEE = "0.00001"
_SEQUENCE = 19048
_NFTOKEN_ID = "00090032B5F762798A53D543A014CAF8B297CFF8F2F937E844B17C9E00000003"


class TestNFTokenCreateOffer(TestCase):
    def test_nftoken_buy_offer_with_zero_amount(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCreateOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                owner=_ANOTHER_ACCOUNT,
                nftoken_id=_NFTOKEN_ID,
                amount="0",
            )

    def test_nftoken_buy_offer_with_negative_amount(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCreateOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                owner=_ANOTHER_ACCOUNT,
                nftoken_id=_NFTOKEN_ID,
                amount="-1",
            )

    def test_nftoken_buy_offer_with_positive_amount(self):
        tx = NFTokenCreateOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            owner=_ANOTHER_ACCOUNT,
            nftoken_id=_NFTOKEN_ID,
            amount="1",
        )
        self.assertTrue(tx.is_valid())

    def test_nftoken_sell_offer_with_zero_amount(self):
        tx = NFTokenCreateOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            amount="0",
            nftoken_id=_NFTOKEN_ID,
            flags=[NFTokenCreateOfferFlag.TF_SELL_NFTOKEN],
        )
        self.assertTrue(tx.is_valid())

    def test_nftoken_sell_offer_with_positive_amount(self):
        tx = NFTokenCreateOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            amount="1",
            nftoken_id=_NFTOKEN_ID,
            flags=[NFTokenCreateOfferFlag.TF_SELL_NFTOKEN],
        )
        self.assertTrue(tx.is_valid())

    def test_destination_is_account(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCreateOffer(
                account=_ACCOUNT,
                destination=_ACCOUNT,
                fee=_FEE,
                owner=_ANOTHER_ACCOUNT,
                sequence=_SEQUENCE,
                nftoken_id=_NFTOKEN_ID,
                amount="1",
            )

    def test_nftoken_buy_offer_without_owner(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCreateOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                amount="1",
                nftoken_id=_NFTOKEN_ID,
            )

    def test_nftoken_buy_offer_with_owner_is_account(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCreateOffer(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                amount="1",
                nftoken_id=_NFTOKEN_ID,
            )

    def test_nftoken_sell_offer_with_owner(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCreateOffer(
                account=_ACCOUNT,
                owner=_ANOTHER_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                amount="1",
                flags=[NFTokenCreateOfferFlag.TF_SELL_NFTOKEN],
                nftoken_id=_NFTOKEN_ID,
            )
