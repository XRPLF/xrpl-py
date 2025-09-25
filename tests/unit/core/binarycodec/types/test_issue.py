from unittest import TestCase

from xrpl.core.binarycodec import XRPLBinaryCodecException
from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types.issue import Issue


class TestIssue(TestCase):
    def test_from_value_xrp(self):
        issue_obj = Issue.from_value({"currency": "XRP"})
        self.assertEqual(issue_obj.to_json(), {"currency": "XRP"})

    def test_from_value_issued_currency(self):
        test_input = {"currency": "USD", "issuer": "rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn"}
        issue_obj = Issue.from_value(test_input)
        expected = {"currency": "USD", "issuer": "rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn"}
        self.assertEqual(issue_obj.to_json(), expected)

    def test_from_value_non_standard_currency(self):
        test_input = {
            "currency": "0123456789ABCDEF0123456789ABCDEF01234567",
            "issuer": "rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn",
        }
        issue_obj = Issue.from_value(test_input)
        expected = {
            "currency": "0123456789ABCDEF0123456789ABCDEF01234567",
            "issuer": "rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn",
        }
        self.assertEqual(issue_obj.to_json(), expected)

    def test_from_value_mpt(self):
        # Test Issue creation for an MPT currency.
        # Use a valid 48-character hex string (24 bytes) for mpt_issuance_id.
        test_input = {
            "mpt_issuance_id": "00001266F19FE2057AE426F72E923CAB3EC8E5BDB3341D9E",
        }
        issue_obj = Issue.from_value(test_input)
        expected = {
            "mpt_issuance_id": "00001266F19FE2057AE426F72E923CAB3EC8E5BDB3341D9E"
        }
        self.assertEqual(issue_obj.to_json(), expected)

    def test_short_mpt_issuance_id(self):
        # A valid mpt_issuance_id is 192 bits long (or 48 characters in hex).
        test_input = {
            "mpt_issuance_id": "A" * 47,
        }
        self.assertRaises(XRPLBinaryCodecException, Issue.from_value, test_input)

    def test_binary_representation_of_mpt_issuance_id(self):
        mpt_issuance_id_in_hex = "00001266F19FE2057AE426F72E923CAB3EC8E5BDB3341D9E"
        test_input = {
            "mpt_issuance_id": mpt_issuance_id_in_hex,
        }
        issue_obj = Issue.from_value(test_input)
        self.assertEqual(
            issue_obj.to_hex(),
            # issuer_account's hex representation
            mpt_issuance_id_in_hex[8:48]
            # the below line is the hex representation of the
            # black-hole-account-id (ACCOUNT_ONE)
            + "0000000000000000000000000000000000000001"
            # sequence number's hex representation
            + mpt_issuance_id_in_hex[6:8]
            + mpt_issuance_id_in_hex[4:6]
            + mpt_issuance_id_in_hex[2:4]
            + mpt_issuance_id_in_hex[0:2],
        )
        self.assertEqual(issue_obj.to_json(), test_input)

    def test_from_parser_xrp(self):
        # Test round-trip: serialize an XRP Issue and then parse it back.
        test_input = {"currency": "XRP"}
        issue_obj = Issue.from_value(test_input)
        # For non-MPT cases, use the hex representation as input to the parser.
        parser = BinaryParser(issue_obj.to_hex())
        issue_from_parser = Issue.from_parser(parser)
        self.assertEqual(issue_from_parser.to_json(), {"currency": "XRP"})

    def test_from_parser_issued_currency(self):
        # Test round-trip: serialize an issued currency Issue and then parse it back.
        test_input = {"currency": "EUR", "issuer": "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD"}
        issue_obj = Issue.from_value(test_input)
        parser = BinaryParser(issue_obj.to_hex())
        issue_from_parser = Issue.from_parser(parser)
        expected = {"currency": "EUR", "issuer": "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD"}
        self.assertEqual(issue_from_parser.to_json(), expected)

    def test_from_parser_non_standard_currency(self):
        # Test round-trip conversion for non-standard currency codes.
        test_input = {
            "currency": "0123456789ABCDEF0123456789ABCDEF01234567",
            "issuer": "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD",
        }
        issue_obj = Issue.from_value(test_input)
        parser = BinaryParser(issue_obj.to_hex())
        issue_from_parser = Issue.from_parser(parser)
        expected = {
            "currency": "0123456789ABCDEF0123456789ABCDEF01234567",
            "issuer": "rLUEXYuLiQptky37CqLcm9USQpPiz5rkpD",
        }
        self.assertEqual(issue_from_parser.to_json(), expected)

    def test_from_parser_mpt(self):
        # Test round-trip: serialize an MPT Issue and then parse it back.
        test_input = {
            "mpt_issuance_id": "00001266F19FE2057AE426F72E923CAB3EC8E5BDB3341D9E",
        }
        issue_obj = Issue.from_value(test_input)
        # Use the hex representation
        parser = BinaryParser(issue_obj.to_hex())
        issue_from_parser = Issue.from_parser(parser)
        expected = {
            "mpt_issuance_id": "00001266F19FE2057AE426F72E923CAB3EC8E5BDB3341D9E"
        }
        self.assertEqual(issue_from_parser.to_json(), expected)

    def test_raises_invalid_value_type(self):
        # Test that providing an invalid input type raises an XRPLBinaryCodecException.
        invalid_value = 1
        self.assertRaises(XRPLBinaryCodecException, Issue.from_value, invalid_value)
