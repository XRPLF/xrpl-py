import time
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import OracleSet
from xrpl.models.transactions.oracle_set import (
    EPOCH_OFFSET,
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
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
            )

        self.assertEqual(
            err.exception.args[0],
            "{'price_data_series': " + "'price_data_series is not set'}",
        )

    def test_exceed_length_price_data_series(self):
        # price_data_series exceeds the mandated length (10 elements)
        with self.assertRaises(XRPLModelException) as err:
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

        self.assertEqual(
            err.exception.args[0],
            "{'price_data_series': 'Field must "
            + "have a length less than or equal to 10'}",
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
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_EMPTY_PROVIDER,
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

        self.assertEqual(
            err.exception.args[0],
            "{'provider': 'Field must have a " + "length greater than 0.'}",
        )

    def test_lengthy_provider_field(self):
        # provider exceeds MAX_ORACLE_PROVIDER characters
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_LENGTHY_PROVIDER,
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

        self.assertEqual(
            err.exception.args[0],
            "{'provider': 'Field must have a " + "length less than or equal to 256.'}",
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
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
                uri="",
                price_data_series=[
                    PriceData(
                        base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                    ),
                    PriceData(
                        base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'uri': 'Field must have a" + " length greater than 0.'}",
        )

    def test_lengthy_uri_field(self):
        # URI exceeds MAX_ORACLE_URI characters
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=int(time.time()),
                uri=("x" * (MAX_ORACLE_URI + 1)),
                price_data_series=[
                    PriceData(
                        base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                    ),
                    PriceData(
                        base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'uri': 'Field must have a" + " length less than or equal to 256.'}",
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
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                last_update_time=int(time.time()),
                asset_class="",
                price_data_series=[
                    PriceData(
                        base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                    ),
                    PriceData(
                        base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'asset_class': 'Field must have" + " a length greater than 0.'}",
        )

    def test_lengthy_asset_class_field(self):
        # URI exceeds MAX_ORACLE_SYMBOL_CLASS characters
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                last_update_time=int(time.time()),
                asset_class=("x" * (MAX_ORACLE_SYMBOL_CLASS + 1)),
                price_data_series=[
                    PriceData(
                        base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                    ),
                    PriceData(
                        base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'asset_class': 'Field must have" + " a length less than or equal to 16'}",
        )

    def test_early_last_update_time_field(self):
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=EPOCH_OFFSET - 1,
                price_data_series=[
                    PriceData(
                        base_asset="XRP", quote_asset="USD", asset_price=740, scale=1
                    ),
                    PriceData(
                        base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'last_update_time': 'LastUpdateTime"
            + " must be greater than or equal to ripple epoch - 946684800 seconds'}",
        )

    # Validity depends on the time of the Last Closed Ledger. This test verifies the
    # validity with respect to the Ripple Epoch time
    def test_valid_last_update_time(self):
        # Note: This test fails in an integration test because it's older than 300s
        # with respect to the LastClosedLedger
        tx = OracleSet(
            account=_ACCOUNT,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=EPOCH_OFFSET,
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

    def test_invalid_price_data_series(self):
        with self.assertRaises(XRPLModelException) as err:
            OracleSet(
                account=_ACCOUNT,
                oracle_document_id=1,
                provider=_PROVIDER,
                asset_class=_ASSET_CLASS,
                last_update_time=EPOCH_OFFSET,
                price_data_series=[
                    PriceData(base_asset="XRP", quote_asset="USD", asset_price=740),
                    PriceData(
                        base_asset="BTC", quote_asset="EUR", asset_price=100, scale=2
                    ),
                ],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'price_data_series': "
            "'Field must have both `AssetPrice` and `Scale` if any are present'}",
        )
