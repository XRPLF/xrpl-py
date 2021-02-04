import json
import os
import unittest

from tests.binarycodec.fixtures.data_driven_fixtures import get_whole_object_tests
from xrpl.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.binarycodec.main import decode, encode

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

invalid_json_x_and_tagged = {
    "OwnerCount": 0,
    "Account": "XVXdn5wEVm5G4UhEHWDPqjvdeH361P7BsapL4m2D2XnPSwT",
    "PreviousTxnLgrSeq": 7,
    "LedgerEntryType": "AccountRoot",
    "PreviousTxnID": "DF530FB14C5304852F20080B0A8EEF3A6BDD044F41F4EBBD68B8B321145FE4FF",
    "Flags": 0,
    "Sequence": 1,
    "Balance": "10000000000",
    "SourceTag": 12345,
}


class TestMainSimple(unittest.TestCase):
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

        self.assertEqual(decode(lower), decode(s))
        self.assertEqual(encode(decode(lower)), s)
        self.assertEqual(encode(json_dict), binary)
        self.assertEqual(decode(encode(json_dict)), json_upper)

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


class TestXAddress(unittest.TestCase):
    def test_xaddress_encode(self):
        self.assertEqual(encode(json_x1), encode(json_r1))

    def test_xaddress_decode(self):
        self.assertEqual(decode(encode(json_x1)), json_r1)

    def test_xaddress_null_tag(self):
        self.assertEqual(encode(json_null_x), encode(json_null_r))

    def test_xaddress_invalid(self):
        with self.assertRaises(ValueError):
            encode(json_invalid_x)

    def test_xaddress_invalid_field(self):
        with self.assertRaises(XRPLBinaryCodecException):
            encode(invalid_json_issuer_tagged)

    def test_xaddress_xaddr_and_dest_tag(self):
        with self.assertRaises(XRPLBinaryCodecException):
            encode(invalid_json_x_and_tagged)


class TestMainFixtures(unittest.TestCase):
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

    def test_codec_fixtures_ledger_data(self):
        pass

    def test_x_codec_fixtures(self):
        self._run_fixtures_test(
            "x-codec-fixtures.json", "transactions", self._check_xaddress_jsons
        )

    def test_whole_object_fixtures(self):
        whole_object_tests = get_whole_object_tests()
        for whole_object in whole_object_tests:
            self.assertEqual(encode(whole_object.tx_json), whole_object.expected_hex)
            self.assertEqual(decode(whole_object.expected_hex), whole_object.tx_json)
