"""Test the get_xchain_claim_id util."""

from __future__ import annotations

import json
from unittest import TestCase

from xrpl.utils import get_xchain_claim_id

path_to_json = "tests/unit/utils/txn_parser/transaction_jsons/"
with open(path_to_json + "XChainCreateClaimID.json", "r") as f:
    fixture = json.load(f)
with open(path_to_json + "XChainCreateClaimID2.json", "r") as f:
    fixture2 = json.load(f)
with open(path_to_json + "nftokenmint_response1.json", "r") as f:
    wrong_fixture = json.load(f)


class TestGetXChainClaimID(TestCase):
    """Test get_xchain_claim_id."""

    def test_decoding_a_valid_xchain_claim_id(self):
        result = get_xchain_claim_id(fixture["meta"])
        expected_xchain_claim_id = "b0"
        self.assertEqual(result, expected_xchain_claim_id)

    def test_a_different_valid_xchain_claim_id(self):
        result = get_xchain_claim_id(fixture2["meta"])
        expected_xchain_claim_id = "ac"
        self.assertEqual(result, expected_xchain_claim_id)

    def test_error_with_wrong_tx_metadata(self) -> None:
        self.assertRaises(TypeError, lambda: get_xchain_claim_id(wrong_fixture["meta"]))

    def test_error_with_raw_instead_of_meta(self) -> None:
        self.assertRaises(TypeError, lambda: get_xchain_claim_id(fixture))
