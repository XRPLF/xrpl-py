from unittest import TestCase

from xrpl.core.binarycodec import decode, encode
from xrpl.core.binarycodec.types.uint64 import UInt64
from xrpl.models.transactions.transaction import Transaction

_ACCOUNT = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

# UInt64 fields that rippled renders in base 10 (SField::kSmdBaseTen)
_BASE10_FIELDS = [
    "MaximumAmount",
    "OutstandingAmount",
    "MPTAmount",
    "LockedAmount",
    "ConfidentialOutstandingAmount",
]

_MPT_ISSUANCE_CREATE = {
    "TransactionType": "MPTokenIssuanceCreate",
    "Account": _ACCOUNT,
    "Fee": "10",
    "Sequence": 1,
    "Flags": 0,
    "SigningPubKey": "",
    "MaximumAmount": "4096",
}


class TestUInt64FieldNames(TestCase):
    def test_base10_fields_decode_as_base10(self):
        for field_name in _BASE10_FIELDS:
            with self.subTest(field_name=field_name):
                blob = encode({"Account": _ACCOUNT, field_name: "4096"})
                self.assertEqual(decode(blob)[field_name], "4096")

    def test_base10_fields_decode_max_value(self):
        for field_name in _BASE10_FIELDS:
            with self.subTest(field_name=field_name):
                blob = encode({"Account": _ACCOUNT, field_name: "9223372036854775807"})
                self.assertEqual(decode(blob)[field_name], "9223372036854775807")

    def test_other_uint64_fields_still_decode_as_hex(self):
        blob = encode({"Account": _ACCOUNT, "OwnerNode": "1000"})
        self.assertEqual(decode(blob)["OwnerNode"], "0000000000001000")

    def test_maximum_amount_round_trip(self):
        blob = encode(_MPT_ISSUANCE_CREATE)
        self.assertIn("0000000000001000", blob)
        self.assertEqual(encode(decode(blob)), blob)

    def test_maximum_amount_round_trip_through_from_blob(self):
        blob = encode(_MPT_ISSUANCE_CREATE)
        transaction = Transaction.from_blob(blob)
        self.assertEqual(transaction.maximum_amount, "4096")
        self.assertEqual(transaction.blob(), blob)

    def test_nested_base10_field_round_trip(self):
        inner = dict(_MPT_ISSUANCE_CREATE, Flags=0x40000000, Fee="0")
        batch = {
            "TransactionType": "Batch",
            "Account": _ACCOUNT,
            "Fee": "10",
            "Sequence": 1,
            "Flags": 0x00010000,
            "RawTransactions": [{"RawTransaction": inner}],
        }
        blob = encode(batch)
        decoded = decode(blob)
        raw = decoded["RawTransactions"][0]["RawTransaction"]
        self.assertEqual(raw["MaximumAmount"], "4096")
        self.assertEqual(encode(decoded), blob)

    def test_locked_amount_encodes_as_base10(self):
        expected = UInt64.from_value("1000")  # 0x1000 == 4096
        self.assertEqual(UInt64.from_value("4096", "LockedAmount"), expected)
        # field header 0x301D (UInt64, nth 29) followed by 0x1000
        blob = encode({"Account": _ACCOUNT, "LockedAmount": "4096"})
        self.assertIn("301D0000000000001000", blob)

    def test_confidential_outstanding_amount_encodes_as_base10(self):
        expected = UInt64.from_value("1000")  # 0x1000 == 4096
        self.assertEqual(
            UInt64.from_value("4096", "ConfidentialOutstandingAmount"), expected
        )
        # field header 0x3020 (UInt64, nth 32) followed by 0x1000
        blob = encode({"Account": _ACCOUNT, "ConfidentialOutstandingAmount": "4096"})
        self.assertIn("30200000000000001000", blob)
