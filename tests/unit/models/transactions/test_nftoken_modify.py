from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.nftoken_modify import NFTokenModify

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_SEQUENCE = 19048

_NFTOKEN_ID = "00090032B5F762798A53D543A014CAF8B297CFF8F2F937E844B17C9E00000003"


class TestNFTokenModify(TestCase):
    def test_nftoken_miss(self):
        with self.assertRaises(XRPLModelException):
            NFTokenModify(
                owner=_ACCOUNT,
                sequence=_SEQUENCE,
                uri=_ACCOUNT * 1000,
            )

    def test_uri_empty(self):
        with self.assertRaises(XRPLModelException):
            NFTokenModify(
                owner=_ACCOUNT,
                sequence=_SEQUENCE,
                nftoken_id=_NFTOKEN_ID,
                uri="",
            )
