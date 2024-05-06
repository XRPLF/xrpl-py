from unittest import TestCase

from xrpl.models import XRPLModelException
from xrpl.models.requests import GetAggregatePrice
from xrpl.models.requests.get_aggregate_price import Oracle

_ACCT_STR_1 = "rBwHKFS534tfG3mATXSycCnX8PAd3XJswj"
_ORACLE_DOC_ID_1 = 1

_ACCT_STR_2 = "rDMKwhm13oJBxBgiWS2SheZhKT5nZP8kez"
_ORACLE_DOC_ID_2 = 2


class TestGetAggregatePrice(TestCase):
    def test_invalid_requests(self):
        """Unit test to validate invalid requests"""
        with self.assertRaises(XRPLModelException):
            # oracles array must contain at least one element
            GetAggregatePrice(
                base_asset="USD",
                quote_asset="XRP",
                oracles=[],
            )

        with self.assertRaises(XRPLModelException):
            # base_asset is missing in the request
            GetAggregatePrice(
                quote_asset="XRP",
                oracles=[
                    Oracle(account=_ACCT_STR_1, oracle_document_id=_ORACLE_DOC_ID_1),
                    Oracle(account=_ACCT_STR_2, oracle_document_id=_ORACLE_DOC_ID_2),
                ],
            )

        with self.assertRaises(XRPLModelException):
            # quote_asset is missing in the request
            GetAggregatePrice(
                base_asset="USD",
                oracles=[
                    Oracle(account=_ACCT_STR_1, oracle_document_id=_ORACLE_DOC_ID_1),
                    Oracle(account=_ACCT_STR_2, oracle_document_id=_ORACLE_DOC_ID_2),
                ],
            )

    def test_valid_request(self):
        """Unit test for validating archetypical requests"""
        request = GetAggregatePrice(
            base_asset="USD",
            quote_asset="XRP",
            oracles=[
                Oracle(account=_ACCT_STR_1, oracle_document_id=_ORACLE_DOC_ID_1),
                Oracle(account=_ACCT_STR_2, oracle_document_id=_ORACLE_DOC_ID_2),
            ],
        )
        self.assertTrue(request.is_valid())

        # specifying trim and time_threshold value
        request = GetAggregatePrice(
            base_asset="USD",
            quote_asset="XRP",
            oracles=[
                Oracle(account=_ACCT_STR_1, oracle_document_id=_ORACLE_DOC_ID_1),
                Oracle(account=_ACCT_STR_2, oracle_document_id=_ORACLE_DOC_ID_2),
            ],
            trim=20,
            time_threshold=10,
        )
        self.assertTrue(request.is_valid())
