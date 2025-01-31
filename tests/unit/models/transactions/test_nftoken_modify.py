from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.nftoken_modify import NFTokenModify

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_SEQUENCE = 19048
_FEE = "0.00001"
_URI = "ABC"
_NFTOKEN_ID = "00090032B5F762798A53D543A014CAF8B297CFF8F2F937E844B17C9E00000003"


class TestNFTokenModify(TestCase):
    def test_nftoken_miss(self):
        with self.assertRaises(XRPLModelException) as error:
            NFTokenModify(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                sequence=_SEQUENCE,
                fee=_FEE,
                uri=_URI,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'nftoken_id': 'nftoken_id is not set'}",
        )

    def test_uri_empty(self):
        with self.assertRaises(XRPLModelException) as error:
            NFTokenModify(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                sequence=_SEQUENCE,
                fee=_FEE,
                nftoken_id=_NFTOKEN_ID,
                uri="",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'uri': 'URI must not be empty string'}",
        )

    def test_uri_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            NFTokenModify(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                sequence=_SEQUENCE,
                fee=_FEE,
                nftoken_id=_NFTOKEN_ID,
                uri=_URI * 1000,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'uri': 'URI must not be longer than 512 characters'}",
        )

    def test_uri_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            NFTokenModify(
                account=_ACCOUNT,
                owner=_ACCOUNT,
                sequence=_SEQUENCE,
                fee=_FEE,
                nftoken_id=_NFTOKEN_ID,
                uri="not-hex-encoded",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'uri': 'URI must be encoded in hex'}",
        )

    def test_valid(self):
        obj = NFTokenModify(
            account=_ACCOUNT,
            owner=_ACCOUNT,
            sequence=_SEQUENCE,
            fee=_FEE,
            uri=_URI,
            nftoken_id=_NFTOKEN_ID,
        )
        self.assertTrue(obj.is_valid())
