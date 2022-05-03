from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import NFTokenAcceptOffer

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_NFTOKEN_BUY_OFFER = "AED08CC1F50DD5F23A1948AF86153A3F3B7593E5EC77D65A02BB1B29E05AB6AF"
_NFTOKEN_SELL_OFFER = "\
    AED08CC1F50DD5F23A1948AF86153A3F3B7593E5EC77D65A02BB1B29E05AB6AE"


class TestNFTokenAcceptOffer(TestCase):
    def test_no_nftoken_sell_offer_nor_buy_offer(self):
        with self.assertRaises(XRPLModelException):
            NFTokenAcceptOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
            )

    def test_nftoken_broker_fee_without_sell_offer(self):
        with self.assertRaises(XRPLModelException):
            NFTokenAcceptOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_buy_offer=_NFTOKEN_BUY_OFFER,
                nftoken_broker_fee="10",
            )

    def test_nftoken_broker_fee_without_buy_offer(self):
        with self.assertRaises(XRPLModelException):
            NFTokenAcceptOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_sell_offer=_NFTOKEN_SELL_OFFER,
                nftoken_broker_fee="10",
            )

    def test_no_nftoken_broker_fee_with_both_offers(self):
        tx = NFTokenAcceptOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            nftoken_sell_offer=_NFTOKEN_SELL_OFFER,
            nftoken_buy_offer=_NFTOKEN_BUY_OFFER,
        )
        self.assertTrue(tx.is_valid())

    def test_zero_nftoken_broker_fee_with_both_offers(self):
        with self.assertRaises(XRPLModelException):
            NFTokenAcceptOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_sell_offer=_NFTOKEN_SELL_OFFER,
                nftoken_buy_offer=_NFTOKEN_BUY_OFFER,
                nftoken_broker_fee="0",
            )

    def test_negative_nftoken_broker_fee_with_both_offers(self):
        with self.assertRaises(XRPLModelException):
            NFTokenAcceptOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                nftoken_sell_offer=_NFTOKEN_SELL_OFFER,
                nftoken_buy_offer=_NFTOKEN_BUY_OFFER,
                nftoken_broker_fee="-10",
            )

    def test_positive_nftoken_broker_fee_with_both_offers(self):
        tx = NFTokenAcceptOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            nftoken_sell_offer=_NFTOKEN_SELL_OFFER,
            nftoken_buy_offer=_NFTOKEN_BUY_OFFER,
            nftoken_broker_fee="10",
        )
        self.assertTrue(tx.is_valid())

    def test_nftoken_sell_offer_without_buy_offer_nor_broker_fee(self):
        tx = NFTokenAcceptOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            nftoken_sell_offer=_NFTOKEN_SELL_OFFER,
        )
        self.assertTrue(tx.is_valid())

    def test_nftoken_buy_offer_without_sell_offer_nor_broker_fee(self):
        tx = NFTokenAcceptOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            nftoken_buy_offer=_NFTOKEN_BUY_OFFER,
        )
        self.assertTrue(tx.is_valid())
