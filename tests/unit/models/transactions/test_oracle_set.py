import time
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import OracleSet
from xrpl.models.transactions.oracle_set import (
    MAX_ORACLE_PROVIDER,
    MAX_ORACLE_SYMBOL_CLASS,
    MAX_ORACLE_URI,
    PriceData,
)

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_PROVIDER = "chainlink"
_ASSET_CLASS = "currency"

_EMPTY_PROVIDER = ""
_LENGTHY_PROVIDER = "X" * (MAX_ORACLE_PROVIDER + 1)


class TestSetOracle(TestCase):
    def test_valid(self):
        tx = OracleSet(
            account=_ACCOUNT,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=int(time.time()),
            price_data_series=[
                PriceData(
                    base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                ),
                PriceData(
                    base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                ),
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_missing_data_series(self):
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
            )

    def test_exceed_length_price_data_series(self):
        # price_data_series exceeds the mandated length (10 elements)
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
                price_data_series=[
                    PriceData(
                        base_asset="XRP", quote_asset="USD1", asset_price=741, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD2", asset_price=742, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD3", asset_price=743, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD4", asset_price=744, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD5", asset_price=745, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD6", asset_price=746, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD7", asset_price=747, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD8", asset_price=748, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD9", asset_price=749, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD10", asset_price=750, scale=1
                    ),
                    PriceData(
                        base_asset="XRP", quote_asset="USD11", asset_price=751, scale=1
                    ),
                ],
            )

    def test_valid_provider_field(self):
        tx = OracleSet(
            account=_ACCOUNT,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=int(time.time()),
            uri="https://some_data_provider.com/path",
            price_data_series=[
                PriceData(
                    base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                ),
                PriceData(
                    base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                ),
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_empty_provider_field(self):
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_EMPTY_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
            )

    def test_lengthy_provider_field(self):
        # provider exceeds MAX_ORACLE_PROVIDER characters
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_LENGTHY_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
            )

    def test_valid_uri_field(self):
        tx = OracleSet(
            account=_ACCOUNT,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=int(time.time()),
            uri="https://some_data_provider.com/path",
            price_data_series=[
                PriceData(
                    base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                ),
                PriceData(
                    base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                ),
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_empty_uri_field(self):
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
                uri="",
            )

    def test_lengthy_uri_field(self):
        # URI exceeds MAX_ORACLE_URI characters
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
                uri=("x" * (MAX_ORACLE_URI + 1)),
            )

    def test_valid_asset_class_field(self):
        tx = OracleSet(
            account=_ACCOUNT,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=int(time.time()),
            uri="https://some_data_provider.com/path",
            price_data_series=[
                PriceData(
                    base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                ),
                PriceData(
                    base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                ),
            ],
        )
        self.assertTrue(tx.is_valid())

    def test_empty_asset_class_field(self):
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                last_update_time=int(time.time()),
                asset_class="",
            )

    def test_lengthy_asset_class_field(self):
        # URI exceeds MAX_ORACLE_SYMBOL_CLASS characters
        with self.assertRaises(XRPLModelException):
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                last_update_time=int(time.time()),
                asset_class=("x" * (MAX_ORACLE_SYMBOL_CLASS + 1)),
            )
