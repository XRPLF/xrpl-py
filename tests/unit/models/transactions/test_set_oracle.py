import time
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import OracleSet

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_PROVIDER = "chainlink"
_ASSET_CLASS = "currency"


class TestSetOracle(TestCase):
    def test_valid(self):
        tx = OracleSet(
            account=_ACCOUNT,
            oracle_document_id=1,
            provider=_PROVIDER,
            asset_class=_ASSET_CLASS,
            last_update_time=int(time.time()),
            price_data_series=[],
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
