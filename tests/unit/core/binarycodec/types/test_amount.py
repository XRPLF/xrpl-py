import xrpl.core.binarycodec.types.amount as amount
from tests.unit.core.binarycodec.types.test_serialized_type import (
    TestSerializedType,
    data_driven_fixtures_for_type,
)
from xrpl.core.binarycodec.binary_wrappers import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.models.amounts.amount import is_issued_currency
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount

# [IOU dict, expected serialized hex]
IOU_CASES = [
    [
        {
            "value": "0",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "80000000000000000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "1",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "D4838D7EA4C680000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "2",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "D4871AFD498D00000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "-2",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "94871AFD498D00000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "value": "2.1",
            "currency": "USD",
            "issuer": "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw",
        },
        "D48775F05A0740000000000000000000000000005553440000"
        "0000008B1CE810C13D6F337DAC85863B3D70265A24DF44",
    ],
    [
        {
            "currency": "XRP",
            "value": "2.1",
            "issuer": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
        },
        "D48775F05A07400000000000000000000000000000000000"
        "000000000000000000000000000000000000000000000000",
    ],
    [
        {
            "currency": "USD",
            "value": "1111111111111111",
            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
        },
        "D843F28CB71571C700000000000000000000000055534400"
        "000000000000000000000000000000000000000000000001",
    ],
]

# [XRP value, hex encoding]
XRP_CASES = [
    ["100", "4000000000000064"],
    ["100000000000000000", "416345785D8A0000"],
]

# [MPT dict, expected serialized hex]
MPT_CASES = [
    [
        {
            "mpt_issuance_id": "0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47",
            "value": "1",
        },
        "6000000000000000010000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47",
    ],
    [
        {
            "value": "9223372036854775807",
            "mpt_issuance_id": "0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47",
        },
        "607FFFFFFFFFFFFFFF0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47",
    ],
]


class TestAmount(TestSerializedType):
    def test_assert_xrp_is_valid_passes(self):
        valid_zero = "0"
        valid_amount = "1000"

        amount.verify_xrp_value(valid_zero)
        amount.verify_xrp_value(valid_amount)

    def test_assert_xrp_is_valid_raises(self):
        invalid_amount_large = "1e20"
        invalid_amount_small = "1e-7"
        invalid_amount_decimal = "1.234"

        self.assertRaises(
            XRPLBinaryCodecException,
            amount.verify_xrp_value,
            invalid_amount_large,
        )
        self.assertRaises(
            XRPLBinaryCodecException,
            amount.verify_xrp_value,
            invalid_amount_small,
        )
        self.assertRaises(
            XRPLBinaryCodecException,
            amount.verify_xrp_value,
            invalid_amount_decimal,
        )

    def test_assert_iou_is_valid(self):
        # { zero, pos, negative } * fractional, large, small
        cases = [
            "0",
            "0.0",
            "1",
            "1.1111",
            "-1",
            "-1.1",
            "1111111111111111.0",
            "-1111111111111111.0",
            "0.00000000001",
            "0.00000000001",
            "-0.00000000001",
            "1.111111111111111e-3",
            "-1.111111111111111e-3",
            "2E+2",
        ]
        for case in cases:
            amount.verify_iou_value(case)

    def test_assert_iou_is_valid_large_integers(self):
        """Test that large integers with trailing zeros are accepted (precision
        is counted by significant digits, not total digits)."""
        valid_cases = [
            # Positive integers with trailing zeros
            "9999999999999999e80",
            "1e80",
            "10000000000000000000000000000",
            # Negative integers with trailing zeros
            "-9999999999999999e80",
            "-1e80",
            "-10000000000000000000000000000",
            # Positive decimals at max precision
            "9999999999999999e-96",
            "1.111111111111111e-81",
            # Negative decimals at max precision
            "-9999999999999999e-96",
            "-1.111111111111111e-81",
        ]
        for case in valid_cases:
            amount.verify_iou_value(case)

    def test_assert_iou_is_valid_rejects_too_many_significant_digits(self):
        """Test that values with more than 16 significant digits are rejected."""
        invalid_cases = [
            # Positive - 17 significant digits
            "99999999999999999e80",
            "1.1111111111111111",
            # Negative - 17 significant digits
            "-99999999999999999e80",
            "-1.1111111111111111",
            # More than 28 significant digits (exceeds default Decimal context)
            "12345678901234567890123456789",
            "-12345678901234567890123456789",
            "1.2345678901234567890123456789",
            "-1.2345678901234567890123456789",
        ]
        for case in invalid_cases:
            self.assertRaises(
                XRPLBinaryCodecException,
                amount.verify_iou_value,
                case,
            )

    def test_raises_invalid_value_type(self):
        invalid_value = [1, 2, 3]
        self.assertRaises(
            XRPLBinaryCodecException, amount.Amount.from_value, invalid_value
        )

    def test_from_value_issued_currency(self):
        for json, serialized in IOU_CASES:
            amount_object = amount.Amount.from_value(json)
            self.assertEqual(amount_object.to_hex(), serialized)

    def test_iou_sub_precision_rounds_to_zero(self):
        """IOU amounts with mantissa below MIN_IOU_MANTISSA must serialize as
        the canonical zero (0x8000000000000000), not as a non-zero amount that
        rippled will reject with 'invalid currency value'."""
        zero_hex = "8000000000000000"
        sub_precision_values = [
            "1e-96",
            "10e-96",
            "100e-96",
            "1000e-96",
            "999999999999999e-96",
        ]
        for value in sub_precision_values:
            with self.subTest(value=value):
                result = amount._serialize_issued_currency_value(value)
                self.assertEqual(
                    result.hex(),
                    zero_hex,
                    f"{value} should serialize to zero but got {result.hex()}",
                )

    def test_from_value_xrp(self):
        for json, serialized in XRP_CASES:
            amount_object = amount.Amount.from_value(json)
            self.assertEqual(amount_object.to_hex(), serialized)

    def test_from_value_mpt(self):
        for json, serialized in MPT_CASES:
            amount_object = amount.Amount.from_value(json)
            self.assertEqual(amount_object.to_hex(), serialized)

    def test_to_json_issued_currency(self):
        for json, serialized in IOU_CASES:
            parser = BinaryParser(serialized)
            amount_object = amount.Amount.from_parser(parser)
            self.assertEqual(amount_object.to_json(), json)

    def test_to_json_xrp(self):
        for json, serialized in XRP_CASES:
            parser = BinaryParser(serialized)
            amount_object = amount.Amount.from_parser(parser)
            self.assertEqual(amount_object.to_json(), json)

    def test_to_json_mpt(self):
        for json, serialized in MPT_CASES:
            parser = BinaryParser(serialized)
            amount_object = amount.Amount.from_parser(parser)
            self.assertEqual(amount_object.to_json(), json)

    def test_fixtures(self):
        for fixture in data_driven_fixtures_for_type("Amount"):
            self.fixture_test(fixture)

    def test_is_issued_currency(self):
        issued_currency = IssuedCurrencyAmount(
            currency="USD", issuer="rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw", value=10
        )
        self.assertTrue(is_issued_currency(issued_currency))
        xrp_amount = "10"
        self.assertFalse(is_issued_currency(xrp_amount))
