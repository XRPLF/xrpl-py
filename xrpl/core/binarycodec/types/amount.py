"""
Codec for serializing and deserializing Amount fields.
See `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
"""
from __future__ import annotations

from decimal import MAX_PREC, Context, Decimal, localcontext
from typing import Any, Dict, Optional, Type, Union

from typing_extensions import Final

from xrpl.constants import (
    IOU_DECIMAL_CONTEXT,
    MAX_IOU_EXPONENT,
    MAX_IOU_MANTISSA,
    MAX_IOU_PRECISION,
    MIN_IOU_EXPONENT,
    MIN_IOU_MANTISSA,
)
from xrpl.core.binarycodec.binary_wrappers import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.models.amounts import IssuedCurrencyAmount

_MAX_DROPS: Final[Decimal] = Decimal("1e17")
_MIN_XRP: Final[Decimal] = Decimal("1e-6")

# other constants:
_NOT_XRP_BIT_MASK: Final[int] = 0x80
_POS_SIGN_BIT_MASK: Final[int] = 0x4000000000000000
_ZERO_CURRENCY_AMOUNT_HEX: Final[int] = 0x8000000000000000
_NATIVE_AMOUNT_BYTE_LENGTH: Final[int] = 8
_CURRENCY_AMOUNT_BYTE_LENGTH: Final[int] = 48


def _contains_decimal(string: str) -> bool:
    """Returns True if the given string contains a decimal point character.

    Args:
        string: The string to check.

    Returns:
        True if the string contains a decimal point character.
    """
    return string.find(".") == -1


def verify_xrp_value(xrp_value: str) -> None:
    """
    Validates the format of an XRP amount.
    Raises if value is invalid.

    Args:
        xrp_value: A string representing an amount of XRP.

    Returns:
        None, but raises if xrp_value is not a valid XRP amount.

    Raises:
        XRPLBinaryCodecException: If xrp_value is not a valid XRP amount.
    """
    # Contains no decimal point
    if not _contains_decimal(xrp_value):
        raise XRPLBinaryCodecException(f"{xrp_value} is an invalid XRP amount.")

    # Within valid range
    decimal = Decimal(xrp_value)
    # Zero is less than both the min and max XRP amounts but is valid.
    if decimal.is_zero():
        return
    if (decimal.compare(_MIN_XRP) == -1) or (decimal.compare(_MAX_DROPS) == 1):
        raise XRPLBinaryCodecException(f"{xrp_value} is an invalid XRP amount.")


def verify_iou_value(issued_currency_value: str) -> None:
    """
    Validates the format of an issued currency amount value.
    Raises if value is invalid.

    Args:
        issued_currency_value: A string representing the "value"
                               field of an issued currency amount.

    Returns:
        None, but raises if issued_currency_value is not valid.

    Raises:
        XRPLBinaryCodecException: If issued_currency_value is invalid.
    """
    decimal_value = Decimal(issued_currency_value)
    if decimal_value.is_zero():
        return
    exponent = decimal_value.as_tuple().exponent
    if (
        (_calculate_precision(issued_currency_value) > MAX_IOU_PRECISION)
        or (exponent > MAX_IOU_EXPONENT)
        or (exponent < MIN_IOU_EXPONENT)
    ):
        raise XRPLBinaryCodecException(
            "Decimal precision out of range for issued currency value."
        )
    _verify_no_decimal(decimal_value)


def _calculate_precision(value: str) -> int:
    """Calculate the precision of given value as a string."""
    decimal_value = Decimal(value, Context(prec=MAX_PREC))
    if decimal_value == decimal_value.to_integral():
        return len(
            decimal_value.quantize(Decimal(1), context=Context(prec=MAX_PREC))
            .as_tuple()
            .digits
        )
    return len(decimal_value.normalize(Context()).as_tuple().digits)


def _verify_no_decimal(decimal: Decimal) -> None:
    """
    Ensure that the value after being multiplied by the exponent
    does not contain a decimal.

    :param decimal: A Decimal object.
    """
    actual_exponent = decimal.as_tuple().exponent
    exponent = Decimal("1e" + str(-(int(actual_exponent) - 15)))
    if actual_exponent == 0:
        int_number_string = "".join([str(d) for d in decimal.as_tuple().digits])
    else:
        # str(Decimal) uses sci notation by default... get around w/ string format
        int_number_string = "{:f}".format(decimal * exponent)
    if not _contains_decimal(int_number_string):
        raise XRPLBinaryCodecException("Decimal place found in int_number_str")


def _serialize_issued_currency_value(value: str) -> bytes:
    """
    Serializes the value field of an issued currency amount to its bytes representation.

    :param value: The value to serialize, as a string.
    :return: A bytes object encoding the serialized value.
    """
    verify_iou_value(value)
    decimal_value = Decimal(value)
    if decimal_value.is_zero():
        return _ZERO_CURRENCY_AMOUNT_HEX.to_bytes(8, byteorder="big")

    # Convert components to integers ---------------------------------------
    sign, digits, exp = decimal_value.as_tuple()
    mantissa = int("".join([str(d) for d in digits]))

    # Canonicalize to expected range ---------------------------------------
    while mantissa < MIN_IOU_MANTISSA and exp > MIN_IOU_EXPONENT:
        mantissa *= 10
        exp -= 1

    while mantissa > MAX_IOU_MANTISSA:
        if exp >= MAX_IOU_EXPONENT:
            raise XRPLBinaryCodecException(
                f"Amount overflow in issued currency value {str(value)}"
            )
        mantissa //= 10
        exp += 1

    if exp < MIN_IOU_EXPONENT or mantissa < MIN_IOU_MANTISSA:
        # Round to zero
        _ZERO_CURRENCY_AMOUNT_HEX.to_bytes(8, byteorder="big", signed=False)

    if exp > MAX_IOU_EXPONENT or mantissa > MAX_IOU_MANTISSA:
        raise XRPLBinaryCodecException(
            f"Amount overflow in issued currency value {str(value)}"
        )

    # Convert to bytes -----------------------------------------------------
    serial = _ZERO_CURRENCY_AMOUNT_HEX  # "Not XRP" bit set
    if sign == 0:
        serial |= _POS_SIGN_BIT_MASK  # "Is positive" bit set
    serial |= (exp + 97) << 54  # next 8 bits are exponents
    serial |= mantissa  # last 54 bits are mantissa

    return serial.to_bytes(8, byteorder="big", signed=False)


def _serialize_xrp_amount(value: str) -> bytes:
    """Serializes an XRP amount.

    Args:
        value: A string representing a quantity of XRP.

    Returns:
        The bytes representing the serialized XRP amount.
    """
    verify_xrp_value(value)
    # set the "is positive" bit (this is backwards from usual two's complement!)
    value_with_pos_bit = int(value) | _POS_SIGN_BIT_MASK
    return value_with_pos_bit.to_bytes(8, byteorder="big")


def _serialize_issued_currency_amount(value: Dict[str, str]) -> bytes:
    """Serializes an issued currency amount.

    Args:
        value: A dictionary representing an issued currency amount

    Returns:
         The bytes representing the serialized issued currency amount.
    """
    amount_string = value["value"]
    amount_bytes = _serialize_issued_currency_value(amount_string)
    currency_bytes = bytes(Currency.from_value(value["currency"]))
    issuer_bytes = bytes(AccountID.from_value(value["issuer"]))
    return amount_bytes + currency_bytes + issuer_bytes


class Amount(SerializedType):
    """Codec for serializing and deserializing Amount fields.
    See `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_
    """

    def __init__(self: Amount, buffer: bytes) -> None:
        """Construct an Amount from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(cls: Type[Amount], value: Union[str, Dict[str, str]]) -> Amount:
        """
        Construct an Amount from an issued currency amount or (for XRP),
        a string amount.

        See `Amount Fields <https://xrpl.org/serialization.html#amount-fields>`_

        Args:
            value: The value from which to construct an Amount.

        Returns:
            An Amount object.

        Raises:
            XRPLBinaryCodecException: if an Amount cannot be constructed.
        """
        with localcontext(IOU_DECIMAL_CONTEXT):
            if isinstance(value, str):
                return cls(_serialize_xrp_amount(value))
            if IssuedCurrencyAmount.is_dict_of_model(value):
                return cls(_serialize_issued_currency_amount(value))

        raise XRPLBinaryCodecException(
            "Invalid type to construct an Amount: expected str or dict,"
            f" received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[Amount], parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Amount:
        """Construct an Amount from an existing BinaryParser.

        Args:
            parser: The parser to construct the Amount object from.
            length_hint: Unused.

        Returns:
            An Amount object.
        """
        parser_first_byte = parser.peek()
        not_xrp = (
            int(parser_first_byte) if parser_first_byte is not None else 0x00
        ) & 0x80
        if not_xrp:
            num_bytes = _CURRENCY_AMOUNT_BYTE_LENGTH
        else:
            num_bytes = _NATIVE_AMOUNT_BYTE_LENGTH
        return cls(parser.read(num_bytes))

    def to_json(self: Amount) -> Union[str, Dict[Any, Any]]:
        """Construct a JSON object representing this Amount.

        Returns:
            The JSON representation of this amount.
        """
        if self.is_native():
            sign = "" if self.is_positive() else "-"
            masked_bytes = (
                int.from_bytes(self.buffer, byteorder="big") & 0x3FFFFFFFFFFFFFFF
            )
            return f"{sign}{masked_bytes}"
        parser = BinaryParser(str(self))
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
        value = Decimal(f"{sign}{int_mantissa}") * Decimal(f"1e{exponent}")

        if value.is_zero():
            value_str = "0"
        else:
            value_str = str(value).rstrip("0").rstrip(".")
        verify_iou_value(value_str)

        return {
            "value": value_str,
            "currency": currency.to_json(),
            "issuer": issuer.to_json(),
        }

    def is_native(self: Amount) -> bool:
        """Returns True if this amount is a native XRP amount.

        Returns:
            True if this amount is a native XRP amount, False otherwise.
        """
        # 1st bit in 1st byte is set to 0 for native XRP
        return (self.buffer[0] & 0x80) == 0

    def is_positive(self: Amount) -> bool:
        """Returns True if 2nd bit in 1st byte is set to 1 (positive amount).

        Returns:
            True if 2nd bit in 1st byte is set to 1 (positive amount),
            False otherwise.
        """
        return (bytes(self)[0] & 0x40) > 0
