import json
import os
from unittest import TestCase

from tests.unit.core.binarycodec.fixtures.data_driven_fixtures import (
    get_whole_object_tests,
)
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.main import (
    decode,
    encode,
    encode_for_multisigning,
    encode_for_signing,
    encode_for_signing_claim,
)

TX_JSON = {
    "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
    "Destination": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    "Flags": (1 << 31),  # tfFullyCanonicalSig
    "Sequence": 1,
    "TransactionType": "Payment",
}

json_x1 = {
    "OwnerCount": 0,
    "Account": "XVXdn5wEVm5G4UhEHWDPqjvdeH361P7BsapL4m2D2XnPSwT",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
}

json_r1 = {
    "OwnerCount": 0,
    "Account": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
    "SourceTag": 12345,
}

json_null_x = {
    "OwnerCount": 0,
    "Account": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Destination": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Issuer": "XVXdn5wEVm5G4UhEHWDPqjvdeH361P4GETfNyyXGaoqBj71",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
}

json_invalid_x = {
    "OwnerCount": 0,
    "Account": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Destination": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Issuer": "XVXdn5wEVm5g4UhEHWDPqjvdeH361P4GETfNyyXGaoqBj71",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
}

json_null_r = {
    "OwnerCount": 0,
    "Account": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Destination": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Issuer": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
}

invalid_json_issuer_tagged = {
    "OwnerCount": 0,
    "Account": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Destination": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Issuer": "XVXdn5wEVm5G4UhEHWDPqjvdeH361P7BsapL4m2D2XnPSwT",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
}

valid_json_x_and_tags = {
    "TransactionType": "Payment",
    "Account": "XVXdn5wEVm5G4UhEHWDPqjvdeH361P7BsapL4m2D2XnPSwT",  # Tag: 12345
    "SourceTag": 12345,
    "Destination": "X7c6XhVKioTMkCS8eEc3PsAoeHTdFjEa1sRcUiULHd265yt",  # Tag: 13
    "DestinationTag": 13,
    "Flags": 0,
    "Sequence": 1,
    "Amount": "1000000",
}
invalid_json_x_and_source_tag = {**valid_json_x_and_tags, "SourceTag": 999}
invalid_json_x_and_dest_tag = {**valid_json_x_and_tags, "DestinationTag": 999}
valid_json_no_x_tags = {
    **valid_json_x_and_tags,
    "Account": "rLs1MzkFWCxTbuAHgjeTZK4fcCDDnf2KRv",
    "Destination": "rso13LJmsQvPzzV3q1keJjn6dLRFJm95F2",
}


signing_json = {
    "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
    "Amount": "1000",
    "Destination": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    "Fee": "10",
    "Flags": 2147483648,
    "Sequence": 1,
    "TransactionType": "Payment",
    "TxnSignature": (
        "30440220718D264EF05CAED7C781FF6DE298DCAC68D002562C9BF3A07C1"
        "E721B420C0DAB02203A5A4779EF4D2CCC7BC3EF886676D803A9981B928D3B8ACA483B80"
        "ECA3CD7B9B"
    ),
    "Signature": (
        "30440220718D264EF05CAED7C781FF6DE298DCAC68D002562C9BF3A07C1E72"
        "1B420C0DAB02203A5A4779EF4D2CCC7BC3EF886676D803A9981B928D3B8ACA483B80ECA"
        "3CD7B9B"
    ),
    "SigningPubKey": (
        "ED5F5AC8B98974A3CA843326D9B88CEBD0560177B973EE0B149F782CFAA06DC66A"
    ),
}


class TestMainSimple(TestCase):
    def test_simple(self):
        encoded = encode(TX_JSON)
        decoded = decode(encoded)
        self.assertEqual(TX_JSON, decoded)

    def test_tx_amount_fee(self):
        tx = {**TX_JSON, "Amount": "1000", "Fee": "10"}
        self.assertEqual(decode(encode(tx)), tx)

    def test_tx_invalid_amt(self):
        tx = {**TX_JSON, "Amount": "1000.789", "Fee": "10.123"}
        with self.assertRaises(XRPLBinaryCodecException):
            encode(tx)

    def test_tx_invalid_amt_invalid_fee(self):
        tx = {**TX_JSON, "Amount": "1000.001", "Fee": "10"}
        with self.assertRaises(XRPLBinaryCodecException):
            encode(tx)

    def test_tx_amount_number(self):
        tx = {**TX_JSON, "Amount": 1000.789}
        with self.assertRaises(XRPLBinaryCodecException):
            encode(tx)

    def test_tx_fee_number(self):
        tx = {**TX_JSON, "Amount": "1000.789", "Fee": 10.123}
        with self.assertRaises(XRPLBinaryCodecException):
            encode(tx)

    def test_lowercase(self):
        s = (
            "1100612200000000240000000125000068652D0000000055B6632D6376A2D9319F"
            "20A1C6DCCB486432D1E4A79951229D4C3DE2946F51D56662400009184E72A00081"
            "140DD319918CD5AE792BF7EC80D63B0F01B4573BBC"
        )
        lower = s.lower()

        binary = (
            "1100612200000000240000000125000000082D00000000550735A0B32B2A3F4C93"
            "8B76D6933003E29447DB8C7CE382BBE089402FF12A03E56240000002540BE40081"
            "1479927BAFFD3D04A26096C0C97B1B0D45B01AD3C0"
        )
        json_dict = {
            "OwnerCount": 0,
            "Account": "rUnFEsHjxqTswbivzL2DNHBb34rhAgZZZK",
            "PreviousTxnLgrSeq": 8,
            "LedgerEntryType": "AccountRoot",
            "PreviousTxnID": (
                "0735A0B32B2A3F4C938B76D6933003E29447DB8C7CE382BBE089402FF12A03E5"
            ).lower(),
            "Flags": 0,
            "Sequence": 1,
            "Balance": "10000000000",
        }

        json_upper = {
            "OwnerCount": 0,
            "Account": "rUnFEsHjxqTswbivzL2DNHBb34rhAgZZZK",
            "PreviousTxnLgrSeq": 8,
            "LedgerEntryType": "AccountRoot",
            "PreviousTxnID": (
                "0735A0B32B2A3F4C938B76D6933003E29447DB8C7CE382BBE089402FF12A03E5"
            ),
            "Flags": 0,
            "Sequence": 1,
            "Balance": "10000000000",
        }

        lowerCaseIntBinary = (
            "11007222001100002501EC24873700000000000000003800000000000000A35506"
            "FC7DE374089D50F81AAE13E7BBF3D0E694769331E14F55351B38D0148018EA62D4"
            "4BF89AC2A40B800000000000000000000000004A50590000000000000000000000"
            "000000000000000000000000000166D6C38D7EA4C6800000000000000000000000"
            "00004A5059000000000047C1258B4B79774B28176324068F759EDE226F68678000"
            "0000000000000000000000000000000000004A505900000000005BBC0F22F61D92"
            "24A110650CFE21CC0C4BE13098"
        )

        lowerCaseIntJson = {
            "Balance": {
                "currency": "JPY",
                "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                "value": "0.3369568318",
            },
            "Flags": 1114112,
            "HighLimit": {
                "currency": "JPY",
                "issuer": "r94s8px6kSw1uZ1MV98dhSRTvc6VMPoPcN",
                "value": "0",
            },
            "HighNode": "a3",
            "LedgerEntryType": "RippleState",
            "LowLimit": {
                "currency": "JPY",
                "issuer": "rfYQMgj3g3Qp8VLoZNvvU35mEuuJC8nCmY",
                "value": "1000000000",
            },
            "LowNode": "0",
            "PreviousTxnID": (
                "06FC7DE374089D50F81AAE13E7BBF3D0E694769331E14F55351B38D0148018EA"
            ).lower(),
            "PreviousTxnLgrSeq": 32253063,
            "index": "000319BAE0A618A7D3BB492F17E98E5D92EA0C6458AFEBED44206B5B4798A840",
        }

        self.assertEqual(decode(lower), decode(s))
        self.assertEqual(encode(decode(lower)), s)
        self.assertEqual(encode(json_dict), binary)
        self.assertEqual(decode(encode(json_dict)), json_upper)
        self.assertEqual(encode(lowerCaseIntJson), lowerCaseIntBinary)

    def test_pseudo_transaction(self):
        json_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "Sequence": 0,
            "Fee": "0",
            "SigningPubKey": "",
            "Signature": "",
        }

        json_blank_acct = {
            "Account": "",
            "Sequence": 0,
            "Fee": "0",
            "SigningPubKey": "",
            "Signature": "",
        }

        binary = (
            "240000000068400000000000000073007600811400000000000000000000000000"
            "00000000000000"
        )

        self.assertEqual(encode(json_dict), binary)
        self.assertEqual(decode(encode(json_dict)), json_dict)
        self.assertEqual(encode(json_blank_acct), binary)
        self.assertEqual(decode(encode(json_blank_acct)), json_dict)

    def test_unl_modify(self):
        v_hash = "EDB6FC8E803EE8EDC2793F1EC917B2EE41D35255618DEB91D3F9B1FC89B75D4539"
        json_dict = {
            "UNLModifyDisabling": 1,
            "LedgerSequence": 67850752,
            "UNLModifyValidator": v_hash,
            "TransactionType": "UNLModify",
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "Sequence": 0,
            "Fee": "0",
            "SigningPubKey": "",
        }
        binary = (
            "120066240000000026040B52006840000000000000007300701321EDB6FC8E803E"
            "E8EDC2793F1EC917B2EE41D35255618DEB91D3F9B1FC89B75D4539810000101101"
        )

        self.assertEqual(encode(json_dict), binary)
        self.assertEqual(decode(encode(json_dict)), json_dict)


class TestXAddress(TestCase):
    def test_xaddress_encode(self):
        self.assertEqual(encode(json_x1), encode(json_r1))

    def test_xaddress_decode(self):
        self.assertEqual(decode(encode(json_x1)), json_r1)

    def test_xaddress_null_tag(self):
        self.assertEqual(encode(json_null_x), encode(json_null_r))

    def test_xaddress_invalid(self):
        with self.assertRaises(XRPLBinaryCodecException):
            encode(json_invalid_x)

    def test_xaddress_invalid_field(self):
        with self.assertRaises(XRPLBinaryCodecException):
            encode(invalid_json_issuer_tagged)

    def test_xaddress_xaddr_and_mismatched_source_tag(self):
        with self.assertRaises(XRPLBinaryCodecException):
            encode(invalid_json_x_and_source_tag)

    def test_xaddress_xaddr_and_mismatched_dest_tag(self):
        with self.assertRaises(XRPLBinaryCodecException):
            encode(invalid_json_x_and_dest_tag)

    def test_xaddress_xaddr_and_matching_source_tag(self):
        self.assertEqual(encode(valid_json_x_and_tags), encode(valid_json_no_x_tags))


class TestMainFixtures(TestCase):
    maxDiff = 1000

    def _check_binary_and_json(self, test):
        test_binary = test["binary"]
        test_json = test["json"]
        with self.subTest(test_binary=test_binary, test_json=test_json):
            self.assertEqual(encode(test_json), test_binary)
            self.assertEqual(decode(test_binary), test_json)

    def _check_xaddress_jsons(self, test):
        x_json = test["xjson"]
        r_json = test["rjson"]
        with self.subTest(x_json=test["xjson"], r_json=test["rjson"]):
            self.assertEqual(encode(x_json), encode(r_json))
            self.assertEqual(decode(encode(x_json)), r_json)

    def _run_fixtures_test(self, filename, category, test_method):
        dirname = os.path.dirname(__file__)
        full_filename = "fixtures/data/" + filename
        absolute_path = os.path.join(dirname, full_filename)
        with open(absolute_path) as fixtures_file:
            fixtures_json = json.load(fixtures_file)
            for test in fixtures_json[category]:
                test_method(test)

    def test_codec_fixtures_account_state(self):
        self._run_fixtures_test(
            "codec-fixtures.json", "accountState", self._check_binary_and_json
        )

    def test_codec_fixtures_transaction(self):
        self._run_fixtures_test(
            "codec-fixtures.json", "transactions", self._check_binary_and_json
        )

    def test_x_codec_fixtures(self):
        self._run_fixtures_test(
            "x-codec-fixtures.json", "transactions", self._check_xaddress_jsons
        )

    def test_whole_object_fixtures(self):
        whole_object_tests = get_whole_object_tests()
        for whole_object in whole_object_tests:
            self.assertEqual(encode(whole_object.tx_json), whole_object.expected_hex)
            self.assertEqual(decode(whole_object.expected_hex), whole_object.tx_json)


class TestMainSigning(TestCase):
    maxDiff = 1000

    def test_single_signing(self):
        expected = (
            "53545800120000228000000024000000016140000000000003E868400000000000"
            "000A7321ED5F5AC8B98974A3CA843326D9B88CEBD0560177B973EE0B149F782CFA"
            "A06DC66A81145B812C9D57731E27A2DA8B1830195F88EF32A3B68314B5F762798A"
            "53D543A014CAF8B297CFF8F2F937E8"
        )
        self.assertEqual(encode_for_signing(signing_json), expected)

    def test_native_claim(self):
        channel = "43904CBFCDCEC530B4037871F86EE90BF799DF8D2E0EA564BC8A3F332E4F5FB1"
        amount = "1000"
        json = {"amount": amount, "channel": channel}

        expected = (
            "434C4D00"
            "43904CBFCDCEC530B4037871F86EE90BF799DF8D2E0EA564BC8A3F332E4F5FB1"
            "00000000000003E8"
        )
        self.assertEqual(encode_for_signing_claim(json), expected)

    def test_ic_claim(self):
        channel = "43904CBFCDCEC530B4037871F86EE90BF799DF8D2E0EA564BC8A3F332E4F5FB1"
        amount = {
            "issuer": "rJZdUusLDtY9NEsGea7ijqhVrXv98rYBYN",
            "currency": "USD",
            "value": "10",
        }
        json = {"amount": amount, "channel": channel}

        expected = (
            "434C4D00"
            "43904CBFCDCEC530B4037871F86EE90BF799DF8D2E0EA564BC8A3F332E4F5FB1"
            "D4C38D7EA4C680000000000000000000000000005553440000000000C0A5ABEF"
            "242802EFED4B041E8F2D4A8CC86AE3D1"
        )
        self.assertEqual(encode_for_signing_claim(json), expected)

    def test_multisig(self):
        signing_account = "rJZdUusLDtY9NEsGea7ijqhVrXv98rYBYN"
        multisig_json = {**signing_json, "SigningPubKey": ""}
        expected = (
            "534D5400120000228000000024000000016140000000000003E868400000000000"
            "000A730081145B812C9D57731E27A2DA8B1830195F88EF32A3B68314B5F762798A"
            "53D543A014CAF8B297CFF8F2F937E8C0A5ABEF242802EFED4B041E8F2D4A8CC86A"
            "E3D1"
        )
        self.assertEqual(
            encode_for_multisigning(multisig_json, signing_account), expected
        )
