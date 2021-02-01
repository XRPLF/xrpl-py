"""
Defines how to serialize and deserialize an amount field.
See `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
"""
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
_POS_SIGN_BIT_MASK = 0x4000000000000000
_ZERO_CURRENCY_AMOUNT_HEX = 0x8000000000000000
_NATIVE_AMOUNT_BYTE_LENGTH = 8
_CURRENCY_AMOUNT_BYTE_LENGTH = 48


def _is_valid_issued_currency_amount(value: Dict) -> bool:
    """
    Determines whether given dictionary represents a valid issued currency amount,
    which must contain exactly "currency", "issuer" and "value" keys.
    """
    if len(value.keys()) != 3:
        return False
    expected_keys = set(["currency", "issuer", "value"])
    for key in expected_keys:
        if not (key in value.keys()):
            return False
    return True


def _assert_is_valid_xrp_value(xrp_value: str) -> None:
    """
    Validates the format of an XRP amount.
    Raises if value is invalid.

    :param xrp_value: A string representing an amount of XRP.
    """
    # Contains no decimal point
    if not (xrp_value.find(".") == -1):
        raise XRPLBinaryCodecException("{} is an invalid XRP amount.".format(xrp_value))

    # Within valid range
    decimal = Decimal(xrp_value)
    # Zero is less than both the min and max XRP amounts but is valid.
    if not decimal.is_zero():
        if (decimal.compare(_MIN_XRP) == -1) or (decimal.compare(_MAX_DROPS) == 1):
            raise XRPLBinaryCodecException(
                "{} is an invalid XRP amount.".format(xrp_value)
            )


def _assert_is_valid_iou_value(issued_currency_value: Decimal) -> None:
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
        _verify_no_decimal(issued_currency_value)


def _verify_no_decimal(decimal: Decimal) -> None:
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


def _serialize_issued_currency_value(value: str) -> bytes:
    """
    Serializes the value field of an issued currency amount to its bytes representation.

    :param value: The value to serialize, as a string.
    :return: A bytes object encoding the serialized value.
    """
    decimal_value = Decimal(value)
    _assert_is_valid_iou_value(decimal_value)
    if decimal_value.is_zero():
        return _ZERO_CURRENCY_AMOUNT_HEX.to_bytes(8, byteorder="big")
    # Convert components to integers ---------------------------------------
    sign, digits, exp = decimal_value.as_tuple()
    mantissa = int("".join([str(d) for d in digits]))

    # Canonicalize to expected range ---------------------------------------
    while mantissa < _MIN_MANTISSA and exp > _MIN_IOU_EXPONENT:
        mantissa *= 10
        exp -= 1

    while mantissa > _MAX_MANTISSA:
        if exp >= _MAX_IOU_EXPONENT:
            raise XRPLBinaryCodecException(
                "Amount overflow in issued currency value {}".format(str(value))
            )
        mantissa //= 10
        exp += 1

    if exp < _MIN_IOU_EXPONENT or mantissa < _MIN_MANTISSA:
        # Round to zero
        _ZERO_CURRENCY_AMOUNT_HEX.to_bytes(8, byteorder="big", signed=False)

    if exp > _MAX_IOU_EXPONENT or mantissa > _MAX_MANTISSA:
        raise XRPLBinaryCodecException(
            "Amount overflow in issued currency value {}".format(str(value))
        )

    # Convert to bytes -----------------------------------------------------
    serial = _ZERO_CURRENCY_AMOUNT_HEX  # "Not XRP" bit set
    if sign == 0:
        serial |= _POS_SIGN_BIT_MASK  # "Is positive" bit set
    serial |= (exp + 97) << 54  # next 8 bits are exponents
    serial |= mantissa  # last 54 bits are mantissa

    return serial.to_bytes(8, byteorder="big", signed=False)


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
            _assert_is_valid_xrp_value(value)
            # set the "is positive" bit (this is backwards from usual two's complement!)
            value_with_pos_bit = int(value) | _POS_SIGN_BIT_MASK
            return cls(value_with_pos_bit.to_bytes(8, byteorder="big"))

        if _is_valid_issued_currency_amount(value):
            amount_string = value["value"]
            amount_bytes = _serialize_issued_currency_value(amount_string)
            currency_bytes = Currency.from_value(value["currency"]).to_bytes()
            issuer_bytes = AccountID.from_value(value["issuer"]).to_bytes()
            return cls(amount_bytes + currency_bytes + issuer_bytes)

        raise XRPLBinaryCodecException("Invalid type to construct an Amount")

    @classmethod
    def from_parser(
        cls, parser: BinaryParser, length_hit: Optional[int] = None
    ) -> Amount:
        """Construct an Amount from an existing BinaryParser."""
        not_xrp = int(parser.peek()) & 0x80
        if not_xrp:
            num_bytes = _CURRENCY_AMOUNT_BYTE_LENGTH
        else:
            num_bytes = _NATIVE_AMOUNT_BYTE_LENGTH
        return cls(parser.read(num_bytes))

    def to_json(self) -> Union[str, Dict]:
        """Construct a JSON object representing this Amount."""
        if self.is_native():
            sign = "" if self.is_positive() else "-"
            masked_bytes = (
                int.from_bytes(self.buffer, byteorder="big") & 0x3FFFFFFFFFFFFFFF
            )
            return "{}{}".format(sign, masked_bytes)
        parser = BinaryParser(self.to_string())
        value_bytes = parser.read(8)
        currency = Currency.from_parser(parser)
        issuer = AccountID.from_parser(parser)
        b1 = value_bytes[0]
        b2 = value_bytes[1]
        is_positive = b1 & 0x40
        sign = "" if is_positive else "-"
        exponent = ((b1 & 0x3F) << 2) + ((b2 & 0xFF) >> 6) - 97
        hex_mantissa = hex(b2 & 0x3F) + value_bytes[2:].hex()
        int_mantissa = int(hex_mantissa[2:], 16)
        value = Decimal("{}{}".format(sign, int_mantissa)) * Decimal(
            "1e{}".format(exponent)
        )

        _assert_is_valid_iou_value(value)
        if value.is_zero():
            value_str = "0"
        else:
            value_str = str(value).rstrip("0").rstrip(".")

        return {
            "value": value_str,
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
