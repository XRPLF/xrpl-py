"""Codec for the Number type.

Note: Much of the ideas and constants in this file are borrowed from the rippled
implementation of the `Number` and `STNumber` class. Please refer to the cpp code.
"""

import re
from typing import Optional, Pattern, Tuple, Type

from typing_extensions import Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.serialized_type import SerializedType

# Limits of representation after normalization of mantissa and exponent
_MIN_MANTISSA = 1000000000000000
_MAX_MANTISSA = 9999999999999999

_MIN_EXPONENT = -32768
_MAX_EXPONENT = 32768

_DEFAULT_VALUE_EXPONENT = -2147483648


def normalize(mantissa: int, exponent: int) -> Tuple[int, int]:
    """Normalize the mantissa and exponent of a number.

    Args:
        mantissa: The mantissa of the input number
        exponent: The exponent of the input number

    Returns:
        A tuple containing the normalized mantissa and exponent
    """
    is_negative = mantissa < 0
    m = abs(mantissa)

    while m < _MIN_MANTISSA and exponent > _MIN_EXPONENT:
        exponent -= 1
        m *= 10

    # Note: This code rounds the normalized mantissa "towards_zero". If your use case
    # needs other rounding modes -- to_nearest, up (or) down, let us know with an
    # appropriate bug report
    while m > _MAX_MANTISSA:
        if exponent >= _MAX_EXPONENT:
            raise XRPLBinaryCodecException("Mantissa and exponent are too large.")

        exponent += 1
        m //= 10

    if is_negative:
        m = -m

    return (m, exponent)


def add32(value: int) -> bytes:
    """Add a 32-bit integer to a bytes object.

    Args:
        value: The integer to add

    Returns:
        A bytes object containing the serialized integer
    """
    serialized_bytes = bytes()
    serialized_bytes += (value >> 24 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 16 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 8 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value & 0xFF).to_bytes(1, "big")

    return serialized_bytes


def add64(value: int) -> bytes:
    """Add a 64-bit integer to a bytes object.

    Args:
        value: The integer to add

    Returns:
        A bytes object containing the serialized integer
    """
    serialized_bytes = bytes()
    serialized_bytes += (value >> 56 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 48 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 40 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 32 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 24 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 16 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value >> 8 & 0xFF).to_bytes(1, "big")
    serialized_bytes += (value & 0xFF).to_bytes(1, "big")

    return serialized_bytes


class NumberParts:
    """Class representing the parts of a number: mantissa, exponent and sign."""

    def __init__(self: Self, mantissa: int, exponent: int, is_negative: bool) -> None:
        """Initialize a NumberParts instance.

        Args:
            mantissa: The mantissa (significant digits) of the number
            exponent: The exponent indicating the position of the decimal point
            is_negative: Boolean indicating if the number is negative
        """
        self.mantissa = mantissa
        self.exponent = exponent
        self.is_negative = is_negative


def extractNumberPartsFromString(value: str) -> NumberParts:
    """Extract the mantissa, exponent and sign from a string.

    Args:
        value: The string to extract the number parts from

    Returns:
        A NumberParts instance containing the mantissa, exponent and sign
    """
    VALID_NUMBER_REGEX: Pattern[str] = re.compile(
        r"^"  # the beginning of the string
        + r"([-+]?)"  # (optional) + or - character
        + r"(0|[1-9][0-9]*)"  # mantissa: a number (no leading zeroes, unless 0)
        + r"(\.([0-9]+))?"  # (optional) decimal point and fractional part
        + r"([eE]([+-]?)([0-9]+))?"  # (optional) E/e, optional + or -, any number
        + r"$"  # the end of the string
    )

    matches = re.fullmatch(VALID_NUMBER_REGEX, value)

    if not matches:
        raise XRPLBinaryCodecException(
            f"Unable to parse number from the input string: {value}"
        )

    # Match fields:
    #   0 = whole input
    #   1 = sign
    #   2 = integer portion
    #   3 = whole fraction (with '.')
    #   4 = fraction (without '.')
    #   5 = whole exponent (with 'e')
    #   6 = exponent sign
    #   7 = exponent number

    is_negative: bool = matches.group(1) == "-"

    # integer only
    if matches.group(3) is None:
        mantissa = int(matches.group(2))
        exponent = 0
    else:
        # handle the fraction input
        mantissa = int(matches.group(2) + matches.group(4))
        exponent = -len(matches.group(4))

    # exponent is specified in the input
    if matches.group(5) is not None:
        if matches.group(6) == "-":
            exponent -= int(matches.group(7))
        else:
            exponent += int(matches.group(7))

    if is_negative:
        mantissa = -mantissa

    return NumberParts(mantissa, exponent, is_negative)


class Number(SerializedType):
    """Codec for serializing and deserializing Number fields."""

    def __init__(self: Self, buffer: bytes) -> None:
        """Construct a Number from given bytes."""
        super().__init__(buffer)

    def display_serialized_hex(self: Self) -> str:
        """Display the serialized hex representation of the number. Utility function
        for debugging.
        """
        return self.buffer.hex().upper()

    @classmethod
    def from_parser(  # noqa: D102
        cls: Type[Self],
        parser: BinaryParser,
        length_hint: Optional[int] = None,  # noqa: ANN401
    ) -> Self:
        # Note: Normalization is not required here. It is assumed that the serialized
        # format was obtained through correct procedure.
        return cls(parser.read(12))

    @classmethod
    def from_value(cls: Type[Self], value: str) -> Self:
        """Construct a Number from a string.

        Args:
            value: The string to construct the Number from

        Returns:
            A Number instance
        """
        number_parts: NumberParts = extractNumberPartsFromString(value)

        # `0` value is represented as a mantissa with 0 and an exponent of
        # _DEFAULT_VALUE_EXPONENT. This is an artifact of the rippled implementation.
        # To ensure compatibility of the codec, we mirror this behavior.
        if (
            number_parts.mantissa == 0
            and number_parts.exponent == 0
            and not number_parts.is_negative
        ):
            normalized_mantissa = 0
            normalized_exponent = _DEFAULT_VALUE_EXPONENT
        else:
            normalized_mantissa, normalized_exponent = normalize(
                number_parts.mantissa, number_parts.exponent
            )

        serialized_mantissa = add64(normalized_mantissa)
        serialized_exponent = add32(normalized_exponent)

        # Number type consists of two cpp std::uint_64t (mantissa) and
        # std::uint_32t (exponent) types which are 8 bytes and 4 bytes respectively
        assert len(serialized_mantissa) == 8
        assert len(serialized_exponent) == 4

        return cls(serialized_mantissa + serialized_exponent)

    def to_json(self: Self) -> str:
        """Convert the Number to a JSON string.

        Note: This method is faithful to rippled's `Number::to_string()` method.
        This ensures API compatibility between rippled and xrpl-py regarding the JSON
        representation of Number objects.

        Returns:
            A JSON string representing the Number
        """
        mantissa = int.from_bytes(self.buffer[:8], byteorder="big", signed=True)
        exponent = int.from_bytes(self.buffer[8:12], byteorder="big", signed=True)

        if exponent == 0:
            return str(mantissa)

        # `0` value is represented as a mantissa with 0 and an
        # exponent of _DEFAULT_VALUE_EXPONENT
        if mantissa == 0 and exponent == _DEFAULT_VALUE_EXPONENT:
            return "0"

        # Use scientific notation for very small or large numbers
        if exponent < -25 or exponent > -5:
            return f"{mantissa}e{exponent}"

        is_negative = mantissa < 0
        mantissa = abs(mantissa)

        # The below padding values are influenced by the exponent range of [-25, -5]
        # in the above if-condition. Values outside of this range use the scientific
        # notation and do not go through the below logic.
        PAD_PREFIX = 27
        PAD_SUFFIX = 23

        raw_value: str = "0" * PAD_PREFIX + str(mantissa) + "0" * PAD_SUFFIX

        # Note: The rationale for choosing 43 is that the highest mantissa has 16
        # digits in decimal representation and the PAD_PREFIX has 27 characters.
        # 27 + 16 sums upto 43 characters.
        OFFSET = exponent + 43
        assert OFFSET > 0, "Exponent is below acceptable limit"

        generate_mantissa: str = raw_value[:OFFSET].lstrip("0")

        if generate_mantissa == "":
            generate_mantissa = "0"

        generate_exponent: str = raw_value[OFFSET:].rstrip("0")
        if generate_exponent != "":
            generate_exponent = "." + generate_exponent

        return f"{'-' if is_negative else ''}{generate_mantissa}{generate_exponent}"
