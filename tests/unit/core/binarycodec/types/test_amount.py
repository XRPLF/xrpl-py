from decimal import Decimal, getcontext, localcontext

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

    def test_iou_underflow_rounds_to_zero(self):
        """Regression test for issue #948.

        A non-zero IOU value whose normalized mantissa falls below
        MIN_IOU_MANTISSA (or whose exponent falls below MIN_IOU_EXPONENT)
        must serialize to the canonical zero amount (only the "Not XRP"
        bit set), and must round-trip back to "0"."""
        issuer = "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw"
        # 8-byte amount ("Not XRP" bit only) + 20-byte currency + 20-byte issuer.
        # Canonical zero layout: only the type bit (bit 63) is set; sign,
        # exponent, and mantissa are all 0. See:
        # https://xrpl.org/docs/references/protocol/binary-format#token-amount-format
        zero_amount_hex = "8000000000000000"
        usd_currency_hex = "0000000000000000000000005553440000000000"
        issuer_hex = "8B1CE810C13D6F337DAC85863B3D70265A24DF44"
        zero_hex = zero_amount_hex + usd_currency_hex + issuer_hex
        underflow_cases = ["1e-82", "1e-96", "-1e-96"]
        for value in underflow_cases:
            iou = {"value": value, "currency": "USD", "issuer": issuer}
            amount_object = amount.Amount.from_value(iou)
            self.assertEqual(
                amount_object.to_hex(),
                zero_hex,
                f"IOU value {value!r} should serialize to canonical zero",
            )
            round_tripped = amount_object.to_json()
            self.assertEqual(round_tripped["value"], "0")
            self.assertEqual(round_tripped["currency"], "USD")
            self.assertEqual(round_tripped["issuer"], issuer)

    def test_iou_to_json_preserves_significant_trailing_zeros(self):
        """IOU values must round-trip exactly when the decoded Decimal
        stringifies as an integer (e.g. ``"1000000000000000"``) or in
        scientific notation (e.g. ``"1E+20"``) — in both shapes the old
        ``rstrip("0")`` chewed into significant digits."""
        issuer = "rDgZZ3wyprx4ZqrGQUkquE9Fs2Xs8XBcdw"
        # Each entry: (input value form, expected decoded value string,
        #              expected 8-byte header in canonical hex).
        trailing_zero_cases = [
            # Integer-form decoded Decimal (canonical internal exponent == 0).
            # ``str(Decimal)`` has no decimal point; the buggy first
            # ``rstrip("0")`` eats every significant trailing zero.
            ("1000000000000000", "1000000000000000", "D8438D7EA4C68000"),
            ("-1000000000000000", "-1000000000000000", "98438D7EA4C68000"),
            # Single trailing zero: the buggy strip eats exactly one digit,
            # producing a small ``x10`` corruption (``9999999999999990`` ->
            # ``999999999999999``) that is plausible-looking and easy to miss
            # under a loose equality check.
            ("9999999999999990", "9999999999999990", "D86386F26FC0FFF6"),
            ("-9999999999999990", "-9999999999999990", "986386F26FC0FFF6"),
            # Interior non-zero digit: proves the strip stops where it lands.
            ("1234567890000000", "1234567890000000", "D84462D53C88D880"),
            # Sci-notation *input* that lands on an integer canonical decode.
            ("25e14", "2500000000000000", "D848E1BC9BF04000"),
            # Large-magnitude (canonical internal exponent pushes outside the
            # fixed-point window): ``str(Decimal)`` emits sci notation like
            # ``"1.000000000000000E+20"`` and the buggy ``rstrip("0")`` shaves
            # a digit off the exponent itself (e.g. ``E+20`` -> ``E+2``). Full
            # mantissa-sign x exponent-sign matrix at |exponent|=20, well
            # within the IOU exponent range and free of any rounding concerns.
            ("1e20", "1" + "0" * 20, "D9838D7EA4C68000"),
            ("-1e20", "-1" + "0" * 20, "99838D7EA4C68000"),
            ("1e-20", "0." + "0" * 19 + "1", "CF838D7EA4C68000"),
            ("-1e-20", "-0." + "0" * 19 + "1", "8F838D7EA4C68000"),
            # Happy-path: fractional trailing zeros (the encoder pads the
            # canonical mantissa to 16 digits, so the decoded Decimal carries
            # 15 fractional digits even for an input like ``"1.2"``). The
            # output must NOT carry those zeros forward; this guards against
            # an over-correction that drops the fractional rstrip entirely.
            ("1.2000000", "1.2", "D4844364C5BB0000"),
            ("-1.2000000", "-1.2", "94844364C5BB0000"),
        ]
        for (
            original_value,
            expected_decoded_value,
            expected_header_hex,
        ) in trailing_zero_cases:
            iou_dict = {
                "value": original_value,
                "currency": "USD",
                "issuer": issuer,
            }
            amount_object = amount.Amount.from_value(iou_dict)
            self.assertEqual(
                amount_object.to_hex()[:16].upper(),
                expected_header_hex,
                f"Encoder produced unexpected header for {original_value!r}",
            )
            round_tripped_iou = amount_object.to_json()
            self.assertEqual(
                round_tripped_iou["value"],
                expected_decoded_value,
                f"Round-trip corrupted {original_value!r}: "
                f"got {round_tripped_iou['value']!r}",
            )
            self.assertEqual(
                Decimal(round_tripped_iou["value"]),
                Decimal(original_value),
                f"Decoded value {round_tripped_iou['value']!r} is "
                f"numerically unequal to input {original_value!r}",
            )

    def test_to_json_iou_independent_of_ambient_decimal_context(self):
        """Regression test for issue #1009.

        ``Amount.to_json()`` reconstructs an IOU's decimal value with
        ``Decimal`` arithmetic. That arithmetic must always use a fixed,
        internal Decimal context (``IOU_DECIMAL_CONTEXT``) and must never
        be affected by -- or leak changes into -- whatever ``Decimal``
        context the calling application happens to have configured via
        ``decimal.getcontext()``."""
        issuer = "rrrrrrrrrrrrrrrrrrrrBZbvji"

        def encode_then_decode(value):
            iou = {"value": value, "currency": "USD", "issuer": issuer}
            return amount.Amount.from_value(iou).to_json()["value"]

        cases = [
            # Exact reproduction from the issue: 16 significant digits that
            # a prec=6 ambient context would silently round to
            # "1234570000000000".
            "1234567890123456",
            # Negative IOU value.
            "-1234567890123456",
            # Large positive exponent (near MAX_IOU_EXPONENT).
            "9999999999999999e80",
            "-9999999999999999e80",
            # Large negative exponent (near MIN_IOU_EXPONENT).
            "9999999999999999e-96",
            "-9999999999999999e-96",
        ]

        for value in cases:
            for prec in (6, 28):
                with localcontext() as ctx:
                    ctx.prec = prec
                    decoded_value = encode_then_decode(value)
                self.assertEqual(
                    Decimal(decoded_value),
                    Decimal(value),
                    f"Ambient Decimal context prec={prec} corrupted "
                    f"round-trip of {value!r}: got {decoded_value!r}",
                )

    def test_to_json_does_not_mutate_ambient_decimal_context(self):
        """``to_json()`` must not leave any lasting change in the caller's
        ambient Decimal context (regression test for issue #1009)."""
        issuer = "rrrrrrrrrrrrrrrrrrrrBZbvji"
        iou = {
            "value": "1234567890123456",
            "currency": "USD",
            "issuer": issuer,
        }
        amount_object = amount.Amount.from_value(iou)

        with localcontext() as ctx:
            ctx.prec = 6
            prec_before = getcontext().prec
            amount_object.to_json()
            prec_after = getcontext().prec
            self.assertEqual(
                prec_before,
                prec_after,
                "to_json() mutated the caller's ambient Decimal context",
            )

    def test_to_json_xrp_and_mpt_unaffected_by_narrowed_ambient_precision(self):
        """XRP-drops and MPT amounts don't go through Decimal
        reconstruction in ``to_json()``, so they must be unaffected by a
        narrowed ambient Decimal context (regression test for #1009)."""
        with localcontext() as ctx:
            ctx.prec = 6

            for json, serialized in XRP_CASES:
                parser = BinaryParser(serialized)
                amount_object = amount.Amount.from_parser(parser)
                self.assertEqual(amount_object.to_json(), json)

            for json, serialized in MPT_CASES:
                parser = BinaryParser(serialized)
                amount_object = amount.Amount.from_parser(parser)
                self.assertEqual(amount_object.to_json(), json)

    def test_to_json_rejects_malformed_iou_mantissa_and_exponent(self):
        """Malformed IOU bytes must raise ``XRPLBinaryCodecException``, never
        decode to a silently altered value or leak a raw ``decimal``
        exception. The 54-bit mantissa field can physically hold 17-digit
        values (up to 2**54 - 1) and the 8-bit biased exponent field values
        up to 158, both outside the canonical IOU range; under the fixed
        16-digit decode context (#1009) an unchecked 17-digit mantissa would
        be silently rounded and an out-of-range exponent would raise
        ``decimal.Overflow``."""
        currency_and_issuer = (
            "0000000000000000000000005553440000000000"  # USD
            "0000000000000000000000000000000000000001"
        )

        def malformed_iou_hex(mantissa, exponent):
            field = exponent + 97
            b1 = 0x80 | 0x40 | (field >> 2)
            b2 = ((field & 0x3) << 6) | ((mantissa >> 48) & 0x3F)
            rest = mantissa & 0xFFFFFFFFFFFF
            return f"{b1:02X}{b2:02X}{rest:012X}" + currency_and_issuer

        # 17-digit mantissa (2**54 - 1) with a legal exponent: must raise,
        # not round to a 16-digit value.
        with self.assertRaises(XRPLBinaryCodecException) as raised:
            amount.Amount.from_parser(
                BinaryParser(malformed_iou_hex(2**54 - 1, -20))
            ).to_json()
        self.assertIn("mantissa", str(raised.exception))

        # Out-of-range exponents (the biased field encodes -97..158, legal
        # range is -96..80) with a canonical mantissa: must raise the codec
        # exception, not decimal.Overflow.
        for exponent in (158, 81, -97):
            with self.assertRaises(XRPLBinaryCodecException) as raised:
                amount.Amount.from_parser(
                    BinaryParser(malformed_iou_hex(10**15, exponent))
                ).to_json()
            self.assertIn("exponent", str(raised.exception))

        # The canonical zero encoding is exempt from the exponent bound
        # (its biased exponent field decodes to -97) and must still decode.
        zero_blob = "80" + "0" * 14 + currency_and_issuer
        zero_value = amount.Amount.from_parser(BinaryParser(zero_blob)).to_json()
        self.assertEqual(zero_value["value"], "0")

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
