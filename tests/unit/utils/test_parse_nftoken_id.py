"""Test the parse_nftoken_id util."""
from __future__ import annotations

from unittest import TestCase

from xrpl import XRPLException
from xrpl.utils.parse_nftoken_id import parse_nftoken_id


class TestParseNFTokenID(TestCase):
    """Test parse_nftoken_id."""

    def test_parse_nftoken_id_successful(self: TestParseNFTokenID) -> None:
        nft_id = "000B0539C35B55AA096BA6D87A6E6C965A6534150DC56E5E12C5D09E0000000C"
        result = parse_nftoken_id(nft_id)
        expected = {
            "nftoken_id": nft_id,
            "flags": 11,
            "transfer_fee": 1337,
            "issuer": "rJoxBSzpXhPtAuqFmqxQtGKjA13jUJWthE",
            "taxon": 1337,
            "sequence": 12,
        }
        self.assertEqual(result, expected)

    def test_parse_nftoken_id_raises(self: TestParseNFTokenID) -> None:
        with self.assertRaises(XRPLException):
            parse_nftoken_id("ABCD")
