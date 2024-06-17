from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import DIDSet

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_VALID_FIELD = "1234567890abcdefABCDEF"
_TOO_LONG_FIELD = "A" * 257
_BAD_HEX_FIELD = "random_non_hex_content"
_BAD_HEX_TOO_LONG_FIELD = "q" * 257


class TestDIDSet(TestCase):
    def test_valid(self):
        tx = DIDSet(
            account=_ACCOUNT,
            did_document=_VALID_FIELD,
            uri=_VALID_FIELD,
            data=_VALID_FIELD,
        )
        self.assertTrue(tx.is_valid())

    def test_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            DIDSet(
                account=_ACCOUNT,
                did_document=_TOO_LONG_FIELD,
            )
            self.assertEqual(
                error.exception.args[0],
                "{'did_document': 'Must be <= 256 characters.'}",
            )

    def test_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            DIDSet(
                account=_ACCOUNT,
                data=_BAD_HEX_FIELD,
            )
            self.assertEqual(
                error.exception.args[0],
                "{'data': 'Must be hex.'}",
            )

    def test_too_long_and_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            DIDSet(
                account=_ACCOUNT,
                uri=_BAD_HEX_TOO_LONG_FIELD,
            )
            self.assertEqual(
                error.exception.args[0],
                "{'uri': 'Must be hex and must be <= 256 characters.'}",
            )

    def test_empty(self):
        with self.assertRaises(XRPLModelException) as error:
            DIDSet(
                account=_ACCOUNT,
            )
            self.assertEqual(
                error.exception.args[0],
                "{'did_set': 'Must have one of `did_document`, `data`, and `uri`.'}",
            )

    def test_delete_data_field(self):
        tx = DIDSet(
            account=_ACCOUNT,
            did_document=_VALID_FIELD,
            uri=_VALID_FIELD,
            data=_VALID_FIELD,
        )
        self.assertTrue(tx.is_valid())

        # delete data field
        tx = DIDSet(
            account=_ACCOUNT,
            data="",
        )

        self.assertTrue(tx.is_valid())
