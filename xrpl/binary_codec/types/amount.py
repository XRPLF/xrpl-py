"""Defines how to serialize and deserialize an amount field."""
from __future__ import annotations

from decimal import Context, Decimal, getcontext, setcontext
from typing import Dict, Optional, Union

from xrpl.binary_codec.binary_wrappers import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.account_id import AccountID
from xrpl.binary_codec.types.currency import Currency
from xrpl.binary_codec.types.serialized_type import SerializedType

# Constants for validating amounts.
_MIN_IOU_EXPONENT = -96
_MAX_IOU_EXPONENT = 80
_MAX_IOU_PRECISION = 16
_MIN_MANTISSA = 10 ** 15
_MAX_MANTISSA = 10 ** 16 - 1

# Configure Decimal
setcontext(
    Context(prec=_MAX_IOU_PRECISION, Emax=_MAX_IOU_EXPONENT, Emin=_MIN_IOU_EXPONENT)
)

_MAX_DROPS = Decimal("1e17")
_MIN_XRP = Decimal("1e-6")

# other constants:
_POS_SIGN_BIT_MASK = "4000000000000000"
_ZERO_CURRENCY_AMOUNT_HEX = "8000000000000000"
_NATIVE_AMOUNT_BYTE_LENGTH = 8
_CURRENCY_AMOUNT_BYTE_LENGTH = 48


# TODO: is there a more Pythonic way to do this? Should an IOU be its own class?
def is_valid_issued_currency_amount(value: Dict) -> bool:
    """
    Determines whether given dictionary represents a valid issued currency amount,
    which must contain exactly "currency", "issuer" and "value" keys.
    """
    if len(value.keys()) != 3:
        return False
    expected_keys = ["currency", "issuer", "value"]
    for key in expected_keys:
        if not (key in value.keys()):
            return False
    return True


# TODO: when it's all writ: are all these docstrings correct?
def assert_xrp_is_valid(xrp_value: str) -> None:
    """
    Validates the format of an XRP amount.
    Raises if value is invalid.

    :param xrp_value: A string representing an integer number of drops of XRP.
    """
    # Contains no decimal point
    if not (xrp_value.find(".") == -1):
        raise XRPLBinaryCodecException("{} is an invalid XRP amount.".format(xrp_value))

    # Within valid range?
    decimal = Decimal(xrp_value)
    # Zero is less than both the min and max XRP amounts but is valid.
    if not decimal.is_zero():
        if (decimal.compare(_MIN_XRP) == -1) or (decimal.compare(_MAX_DROPS) == 1):
            raise XRPLBinaryCodecException(
                "{} is an invalid XRP amount.".format(xrp_value)
            )


def assert_iou_is_valid(issued_currency_value: Decimal) -> None:
    """
    Validates the format of an issued currency amount value.
    Raises if value is invalid.

    :param issued_currency_value: A Decimal object representing the "value"
                                    field of an issued currency amount.
    """
    if not issued_currency_value.is_zero():
        precision = getcontext().prec
        exponent = issued_currency_value.as_tuple().exponent
        if (
            (precision > _MAX_IOU_PRECISION)
            or (exponent > _MAX_IOU_EXPONENT)
            or (exponent < _MIN_IOU_EXPONENT)
        ):
            raise XRPLBinaryCodecException(
                "Decimal precision out of range for issued currency value."
            )
        verify_no_decimal(issued_currency_value)


def verify_no_decimal(decimal: Decimal) -> None:
    """
    Ensure that the value after being multiplied by the exponent
    does not contain a decimal.

    :param decimal: A Decimal object.
    """
    actual_exponent = decimal.as_tuple().exponent
    exponent = Decimal("1e" + str(-(int(actual_exponent) - 15)))
    # str(Decimal) uses sci notation by default... get around w/ string format
    int_number_string = "{:f}".format(decimal * exponent)
    if not (int_number_string.find(".") == -1):
        raise XRPLBinaryCodecException("Decimal place found in int_number_str")


class Amount(SerializedType):
    """Defines how to serialize and deserialize an amount.
    See `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
    """

    def __init__(self, buffer: bytes) -> None:
        """Construct an Amount from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(cls, value: Union[str, Dict]) -> Amount:
        """
        Construct an Amount from an issued currency amount or (for XRP),
        a string amount.

        See `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
        """
        if isinstance(value, str):
            assert_xrp_is_valid(value)
            raw_bytes = int(value).to_bytes(8, byteorder="big", signed=False)
            # set the "is positive" bit (this is backwards from usual two's complement!)
            raw_bytes |= _POS_SIGN_BIT_MASK
            return cls(raw_bytes)

        if is_valid_issued_currency_amount(value):
            decimal_value = Decimal(value["value"])
            assert_iou_is_valid(decimal_value)
            if decimal_value.is_zero():
                amount_bytes = bytes.fromhex(_ZERO_CURRENCY_AMOUNT_HEX)
            else:
                # Convert components to integers ---------------------------------------
                sign, digits, exp = decimal_value.as_tuple()
                mantissa = int("".join([str(d) for d in digits]))

                # Canonicalize to expected range ---------------------------------------
                while mantissa < _MIN_MANTISSA and exp > _MIN_IOU_EXPONENT:
                    mantissa *= 10
                    exp -= 1

                while mantissa > _MAX_MANTISSA:
                    if exp >= _MAX_IOU_EXPONENT:
                        raise ValueError("amount overflow")
                    mantissa //= 10
                    exp += 1

                if exp < _MIN_IOU_EXPONENT or mantissa < _MIN_MANTISSA:
                    # Round to zero
                    (0x8000000000000000).to_bytes(8, byteorder="big", signed=False)

                if exp > _MAX_IOU_EXPONENT or mantissa > _MAX_MANTISSA:
                    raise ValueError("amount overflow")

                # Convert to bytes -----------------------------------------------------
                serial = 0x8000000000000000  # "Not XRP" bit set
                if sign == 0:
                    serial |= 0x4000000000000000  # "Is positive" bit set
                serial |= (exp + 97) << 54  # next 8 bits are exponent
                serial |= mantissa  # last 54 bits are mantissa

                amount_bytes = serial.to_bytes(8, byteorder="big", signed=False)

            currency_bytes = Currency.from_value(value["currency"]).to_bytes()
            issuer_bytes = AccountID.from_value(value["issuer"]).to_bytes()
            return cls(amount_bytes + currency_bytes + issuer_bytes)

        raise XRPLBinaryCodecException("Invalid type to construct an Amount")

    @classmethod
    def from_parser(
        cls, parser: BinaryParser, length_hit: Optional[int] = None
    ) -> Amount:
        """Construct an Amount from an existing BinaryParser."""
        is_xrp = int(parser.peek()) & 0x08
        if is_xrp:
            num_bytes = 48
        else:
            num_bytes = 8
        return cls(parser.read(num_bytes))

    def to_json(self):
        """Construct a JSON object representing this Amount."""
        if self.is_native():
            raw_bytes = bytes(self.buffer[0] & 0x40) + self.buffer[1:]
            sign = "" if self.is_positive() else "-"
            return "{}{}".format(
                sign, int.from_bytes(raw_bytes, byteorder="big", signed=False)
            )
        parser = BinaryParser(self.to_string())
        mantissa = parser.read(8)
        currency = Currency.from_parser(parser)
        issuer = AccountID.from_parser(parser)
        b1 = mantissa[0]
        b2 = mantissa[1]
        is_positive = b1 & 0x04
        sign = "" if is_positive else "-"
        exponent = ((b1 & 0x3F) << 2) + ((b2 & 0xFF) >> 6) - 97
        mantissa = bytes(1) + bytes(b2 & 0x3F) + mantissa[2:]
        value = Decimal("{}0x{}".format(sign, mantissa.hex())) * Decimal(
            "1e{}".format(exponent)
        )
        assert_iou_is_valid(value)
        return {
            "value": str(value),
            "currency": currency.to_json(),
            "issuer": issuer.to_json(),
        }

    def is_native(self) -> bool:
        """Returns True if this amount is a native XRP amount."""
        # 1st bit in 1st byte is set to 0 for native XRP
        return (self.buffer[0] & 0x80) == 0

    def is_positive(self) -> bool:
        """Returns True if 2nd bit in 1st byte is set to 1 (positive amount)."""
        return (self.to_bytes()[0] & 0x40) > 0
