"""Codec for the Number type.

Note: Much of the ideas and constants in this file are borrowed from the rippled
implementation of the `Number` and `STNumber` class. Please refer to the cpp code.
"""

import math
import re
from typing import Optional, Pattern, Tuple, Type

from typing_extensions import Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.serialized_type import SerializedType

_DEBUG = False

# Limits of representation after normalization of mantissa and exponent
# This minimum and maximum correspond to the "MantissaRange::large" values. This is the
# default range of the Number type. However, legacy transactions make use of the
# MantissaRange::small i.e. [10^15, 10^16-1].
_MIN_MANTISSA = 1_000_000_000_000_000_000
_MAX_MANTISSA = _MIN_MANTISSA * 10 - 1
_MAX_REP = 9223372036854775807

_MANTISSA_LOG = math.log10(_MIN_MANTISSA)

_MIN_EXPONENT = -32768
_MAX_EXPONENT = 32768

# the below value is used for the representation of Number zero
_DEFAULT_VALUE_EXPONENT = -2147483648


def normalize(mantissa: int, exponent: int) -> Tuple[int, int]:
    """Normalize the mantissa and exponent of a number.

    Args:
        mantissa: The mantissa of the input number
        exponent: The exponent of the input number

    Returns:
        A tuple containing the normalized mantissa and exponent
    """
    if mantissa == 0:
        return (0, _DEFAULT_VALUE_EXPONENT)

    is_negative = mantissa < 0
    m = abs(mantissa)

    while m < _MIN_MANTISSA and exponent > _MIN_EXPONENT:
        exponent -= 1
        m *= 10

    # Note: This code rounds the normalized mantissa "towards_zero". If your use case
    # needs other rounding modes -- to_nearest, up (or) down, let us know with an
    # appropriate bug report. This implementation loses precision for input values with
    # more than 19 digits.
    while m > _MAX_MANTISSA:
        if exponent >= _MAX_EXPONENT:
            raise XRPLBinaryCodecException("Mantissa and exponent are too large.")

        exponent += 1
        m //= 10

    if exponent < _MIN_EXPONENT or m < _MIN_MANTISSA:
        print(
            "Underflow detected: Value too small to represent hence defaulting to zero."
        )
        return (0, _DEFAULT_VALUE_EXPONENT)

    if m > _MAX_REP:
        if _DEBUG:
            print(
                "Mantissa "
                + str(m)
                + " is larger than _MAX_REP. Mantissa will be reduced whilst the"
                + " exponent is increased by an order of magnitude.\n"
            )
        if exponent > _MAX_EXPONENT:
            raise XRPLBinaryCodecException(
                "Overflow: Mantissa and exponent are too large."
            )
        # Note: Due to lack of rounding support, there is a loss of precision of 1
        # digit in this step
        m = m // 10
        exponent += 1

    if exponent > _MAX_EXPONENT:
        raise XRPLBinaryCodecException("Overflow: Mantissa and exponent are too large.")

    if is_negative:
        m = -m

    if _DEBUG:
        print("\n================================================")
        print("Mantissa after Normalization: ", m)
        print("Exponent after Normalization: ", exponent)
        print("================================================")

    return (m, exponent)


def add32(value: int) -> bytes:
    """Add a 32-bit integer to a bytes object.

    Args:
        value: The integer to add

    Returns:
        A bytes object containing the serialized integer
    """
    return value.to_bytes(4, byteorder="big", signed=True)


def add64(value: int) -> bytes:
    """Add a 64-bit integer to a bytes object.

    Args:
        value: The integer to add

    Returns:
        A bytes object containing the serialized integer
    """
    return value.to_bytes(8, byteorder="big", signed=True)


def get64(buffer: bytes) -> int:
    """Obtain a 64-bit integer from a bytes object.

    Args:
        value: The bytes buffer containing the serialized representation of the Number
        data type

    Returns:
        A transformed int object
    """
    return int.from_bytes(buffer, byteorder="big", signed=True)


def get32(buffer: bytes) -> int:
    """Obtain a 32-bit integer from a bytes object.

    Args:
        value: The bytes buffer containing the serialized representation of the Number
        data type

    Returns:
        A transformed int object
    """
    return int.from_bytes(buffer, byteorder="big", signed=True)


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

    if _DEBUG:
        print("================================================")
        print("Mantissa extracted from number parts: ", mantissa)
        print("Exponent extracted from number parts: ", exponent)
        print("is_negative extracted from number parts: ", is_negative)
        print("================================================")
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

    @classmethod
    def from_mantissa_exponent(cls: Type[Self], _mantissa: int, _exponent: int) -> Self:
        """Construct a Number from mantissa and exponent values. Note: This method is
        only used in unit tests.

        Args:
            value: The string to construct the Number from

        Returns:
            A Number instance
        """
        normalized_mantissa, normalized_exponent = normalize(_mantissa, _exponent)
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
        if exponent != 0 and (
            exponent < -(_MANTISSA_LOG + 10) or exponent > -(_MANTISSA_LOG - 10)
        ):
            while mantissa != 0 and mantissa % 10 == 0 and exponent < _MAX_EXPONENT:
                mantissa = mantissa // 10
                exponent += 1

            return f"{mantissa}e{exponent}"

        is_negative = mantissa < 0
        mantissa = abs(mantissa)

        PAD_PREFIX = int(_MANTISSA_LOG + 12)
        PAD_SUFFIX = int(_MANTISSA_LOG + 8)

        raw_value: str = "0" * PAD_PREFIX + str(mantissa) + "0" * PAD_SUFFIX

        # In cases where the mantissa exceeds _MAX_REP, the number of digits in the
        # decimal representation of `mantissa` is one less than _MANTISSA_LOG
        OFFSET = int(exponent + PAD_PREFIX + len(str(mantissa)))
        assert OFFSET > 0, "Exponent is below acceptable limit"

        generate_mantissa: str = raw_value[:OFFSET].lstrip("0")

        if generate_mantissa == "":
            generate_mantissa = "0"

        generate_exponent: str = raw_value[OFFSET:].rstrip("0")
        if generate_exponent != "":
            generate_exponent = "." + generate_exponent

        return f"{'-' if is_negative else ''}{generate_mantissa}{generate_exponent}"
