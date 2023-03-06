"""Test the parse_nftoken_id util."""
from __future__ import annotations
import json

from unittest import TestCase

from xrpl import XRPLException
from xrpl.utils.get_nftoken_id import get_nftoken_id

path_to_json = "tests/unit/utils/txn_parser/transaction_jsons/"
with open(path_to_json + "nftokenmint_response1.json", "r") as infile:
    nftokenmint_response1 = json.load(infile)
with open(path_to_json + "nftokenmint_response2.json", "r") as infile:
    nftokenmint_response2 = json.load(infile)


class TestGetNFTokenID(TestCase):
    """Test get_nftoken_id."""

    '''
    it('decode a valid NFTokenID', function () {
        const result = getNFTokenID(NFTokenResponse.meta)
        const expectedNFTokenID =
        '00081388DC1AB4937C899037B2FDFC3CB20F6F64E73120BB5F8AA66A00000228'
        assert.equal(result, expectedNFTokenID)
    })
    '''
    def test_decoding_a_valid_nftoken_id(self: TestGetNFTokenID):
        result = get_nftoken_id(nftokenmint_response1["meta"])
        expected_nftoken_id = "00081388DC1AB4937C899037B2FDFC3CB20F6F64E73120BB5F8AA66A00000228"
        self.assertEqual(result, expected_nftoken_id)

    '''
    it('decode a different valid NFTokenID', function () {
        const result = getNFTokenID(NFTokenResponse2.meta)
        const expectedNFTokenID =
        '0008125CBE4B401B2F62ED35CC67362165AA813CCA06316FFA766254000003EE'
        assert.equal(result, expectedNFTokenID)
    })
    '''
    def test_a_different_valid_nftokenmint_metadata(self: TestGetNFTokenID):
        result = get_nftoken_id(nftokenmint_response2["meta"])
        expected_nftoken_id = "0008125CBE4B401B2F62ED35CC67362165AA813CCA06316FFA766254000003EE"
        self.assertEqual(result, expected_nftoken_id)

    '''
    it('fails with nice error when given raw response instead of meta', function () {
        assert.throws(() => {
        // @ts-expect-error - Validating error for javascript users
        const _ = getNFTokenID(NFTokenResponse)
        }, /^Unable to parse the parameter given to getNFTokenID.*/u)
    })
    # TODO: Get rid of the in-line code comments
    '''
    def test_error_when_given_raw_instead_of_meta(self: TestGetNFTokenID) -> None:
        self.assertRaises(TypeError, lambda : get_nftoken_id(nftokenmint_response1))