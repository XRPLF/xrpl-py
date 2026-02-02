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


class NumberGuard:
    """Guard class for temporarily adding extra digits of precision to an operation.

    This enables the final result to be correctly rounded to the internal precision
    of Number. The guard stores 16 decimal digits using 4 bits per digit in a 64-bit
    integer.

    Ported from rippled's Number::Guard class in Number.cpp.
    """

    # Constant representing exactly half (0.5) in the guard digit representation
    _HALF = 0x5000_0000_0000_0000

    def __init__(self: Self) -> None:
        """Initialize a NumberGuard instance with zero guard digits."""
        self._digits: int = 0  # 16 decimal guard digits (4 bits each)
        # Note: _xbit is useful only when more than 16 digits have been pushed into NumberGuard.
        self._xbit: bool = False  # has a non-zero digit been shifted off the end
        self._sbit: bool = False  # the sign of the guard digits (True = negative)

    def set_positive(self: Self) -> None:
        """Set the sign bit to positive."""
        self._sbit = False

    def set_negative(self: Self) -> None:
        """Set the sign bit to negative."""
        self._sbit = True

    def is_negative(self: Self) -> bool:
        """Check if the guard digits represent a negative value.

        Returns:
            True if negative, False if positive.
        """
        return self._sbit

    def push(self: Self, d: int) -> None:
        """Push a digit into the guard, shifting existing digits right.

        Args:
            d: The digit to push (0-9).
        """
        # Track if any non-zero digit is being shifted off
        self._xbit = self._xbit or ((self._digits & 0x0000_0000_0000_000F) != 0)
        # Shift right by 4 bits (one digit)
        self._digits >>= 4
        # Add new digit at the top (most significant position)
        self._digits |= (d & 0x0000_0000_0000_000F) << 60

        if _DEBUG:
            print("NumberGuard INFO: Pushing digit: ", d)
            print("NumberGuard INFO: Guard digits after pushing: ", hex(self._digits))

    def pop(self: Self) -> int:
        """Pop the most significant digit from the guard.

        Returns:
            The most significant digit (0-9).
        """
        d = (self._digits & 0xF000_0000_0000_0000) >> 60
        self._digits <<= 4
        # Mask to 64 bits (Python ints have unlimited precision)
        self._digits &= 0xFFFF_FFFF_FFFF_FFFF

        if _DEBUG:
            print("NumberGuard INFO: Popping digit: ", d)
            print("NumberGuard INFO: Guard digits after popping: ", hex(self._digits))

        return d

    def round(self: Self) -> int:
        """Determine the rounding direction for 'to_nearest' mode.

        This implements "round half to even" (banker's rounding):
        - Returns 1 if guard digits are greater than half (round up)
        - Returns -1 if guard digits are less than half (round down)
        - Returns 0 if guard digits are exactly half (caller decides based on even/odd)

        Returns:
            1 for round up, -1 for round down, 0 for exactly half.
        """
        if self._digits > self._HALF:
            return 1
        if self._digits < self._HALF:
            return -1
        if self._xbit:
            # Exactly half but more non-zero digits were shifted off
            return 1
        return 0

    def bring_into_range(
        self: Self,
        is_negative: bool,
        mantissa: int,
        exponent: int,
        min_mantissa: int,
        min_exponent: int,
        default_exponent: int,
        max_rep: int,
    ) -> Tuple[bool, int, int]:
        """Bring mantissa back into the min/max mantissa range after rounding.

        Note: Unlike the C++ implementation which uses uint64_t internally,
        Python serializes as signed int64. We skip scaling up if it would
        exceed max_rep.

        Args:
            is_negative: Whether the number is negative.
            mantissa: The mantissa value.
            exponent: The exponent value.
            min_mantissa: The minimum allowed mantissa.
            min_exponent: The minimum allowed exponent.
            default_exponent: The default exponent for zero values.
            max_rep: The maximum representable value for signed int64.

        Returns:
            A tuple of (is_negative, mantissa, exponent) after adjustment.
        """
        # Only scale up if it won't exceed max_rep (Python uses signed int64)
        if mantissa < min_mantissa and mantissa * 10 <= max_rep:
            mantissa *= 10
            exponent -= 1

        if exponent < min_exponent:
            # Underflow to zero
            is_negative = False
            mantissa = 0
            exponent = default_exponent

        if _DEBUG:
            print(
                "NumberGuard INFO: After bringing mantissa into range: ",
                is_negative,
                mantissa,
                exponent,
            )

        return (is_negative, mantissa, exponent)

    def do_round_up(
        self: Self,
        is_negative: bool,
        mantissa: int,
        exponent: int,
        min_mantissa: int,
        max_mantissa: int,
        max_rep: int,
        max_exponent: int,
        default_exponent: int,
        min_exponent: int,
    ) -> Tuple[bool, int, int]:
        """Apply rounding and adjust mantissa/exponent to stay in valid range.

        This method rounds up when appropriate (based on guard digits) and ensures
        the result stays within the valid mantissa range.

        Args:
            is_negative: Whether the number is negative.
            mantissa: The mantissa value.
            exponent: The exponent value.
            min_mantissa: The minimum allowed mantissa.
            max_mantissa: The maximum allowed mantissa.
            max_rep: The maximum representable value.
            max_exponent: The maximum allowed exponent.
            default_exponent: The default exponent for zero values.
            min_exponent: The minimum allowed exponent.

        Returns:
            A tuple of (is_negative, mantissa, exponent) after rounding.

        Raises:
            XRPLBinaryCodecException: If the exponent overflows.
        """
        r = self.round()
        if r == 1 or (r == 0 and (mantissa & 1) == 1):
            mantissa += 1
            # Ensure mantissa after incrementing fits within both the
            # min/max mantissa range and is a valid "rep".
            if mantissa > max_mantissa or mantissa > max_rep:
                mantissa //= 10
                exponent += 1

        is_negative, mantissa, exponent = self.bring_into_range(
            is_negative,
            mantissa,
            exponent,
            min_mantissa,
            min_exponent,
            default_exponent,
            max_rep,
        )

        if exponent > max_exponent:
            raise XRPLBinaryCodecException(
                "Overflow: exponent too large after rounding"
            )

        if _DEBUG:
            print("NumberGuard INFO: Rounding up: ", is_negative, mantissa, exponent)

        return (is_negative, mantissa, exponent)


# Limits of representation after normalization of mantissa and exponent
# This minimum and maximum correspond to the "MantissaRange::large" values. This is the
# default range of the Number type. However, legacy transactions make use of the
# MantissaRange::small i.e. [10^15, 10^16-1].
_MIN_MANTISSA = 1_000_000_000_000_000_000
_MAX_MANTISSA = _MIN_MANTISSA * 10 - 1
_MAX_REP = 9_223_372_036_854_775_807

_MANTISSA_LOG = math.log10(_MIN_MANTISSA)

_MIN_EXPONENT = -32768
_MAX_EXPONENT = 32768

# the below value is used for the representation of Number zero
_DEFAULT_VALUE_EXPONENT = -2147483648


def normalize(mantissa: int, exponent: int) -> Tuple[int, int]:
    """Normalize the mantissa and exponent of a number.

    This implementation matches rippled's doNormalize function. In case of a tie, it
    rounds up the mantissa.

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

    # Scale up mantissa while it's below minimum
    while m < _MIN_MANTISSA and exponent > _MIN_EXPONENT:
        m *= 10
        exponent -= 1

    # Create guard for rounding
    guard = NumberGuard()
    if is_negative:
        guard.set_negative()

    # Scale down mantissa while it's above maximum, pushing digits to guard
    while m > _MAX_MANTISSA:
        if exponent >= _MAX_EXPONENT:
            raise XRPLBinaryCodecException("Number::normalize overflow 1")
        guard.push(m % 10)
        m //= 10
        exponent += 1

    # Handle underflow
    if exponent < _MIN_EXPONENT or m < _MIN_MANTISSA:
        return (0, _DEFAULT_VALUE_EXPONENT)

    # When using largeRange, m needs to fit within int64 (maxRep).
    # Cut it down here so rounding is done while it's smaller.
    if m > _MAX_REP:
        if exponent >= _MAX_EXPONENT:
            raise XRPLBinaryCodecException("Number::normalize overflow 1.5")
        guard.push(m % 10)
        m //= 10
        exponent += 1

    # Apply rounding using the guard
    is_negative, m, exponent = guard.do_round_up(
        is_negative,
        m,
        exponent,
        _MIN_MANTISSA,
        _MAX_MANTISSA,
        _MAX_REP,
        _MAX_EXPONENT,
        _DEFAULT_VALUE_EXPONENT,
        _MIN_EXPONENT,
    )

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


def get64(buffer: bytes) -> int:
    """Obtain a 64-bit integer from a bytes object.

    Args:
        buffer: The bytes buffer containing the serialized representation of the Number
        data type

    Returns:
        A transformed int object
    """
    return int.from_bytes(buffer, byteorder="big", signed=True)


def get32(buffer: bytes) -> int:
    """Obtain a 32-bit integer from a bytes object.

    Args:
        buffer: The bytes buffer containing the serialized representation of the Number
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

    def round_to_integer(self: Self) -> int:
        """Round the Number to an integer using 'to_nearest' rounding mode.

        This implements "round half to even" (banker's rounding), matching
        rippled's Number::operator rep() with to_nearest rounding mode.

        Returns:
            The rounded integer value.
        """
        mantissa = int.from_bytes(self.buffer[:8], byteorder="big", signed=True)
        exponent = int.from_bytes(self.buffer[8:12], byteorder="big", signed=True)

        # Handle zero
        if mantissa == 0:
            return 0

        is_negative = mantissa < 0
        drops = abs(mantissa)

        guard = NumberGuard()
        if is_negative:
            guard.set_negative()

        # Shift digits into guard while adjusting exponent toward zero
        while exponent < 0:
            guard.push(drops % 10)
            drops //= 10
            exponent += 1

        # Scale up for positive exponents
        while exponent > 0:
            drops *= 10
            exponent -= 1

        # Apply rounding based on guard digits
        r = guard.round()
        if r == 1 or (r == 0 and (drops & 1) == 1):
            # Round up (away from zero for the absolute value)
            drops += 1

        # Apply sign
        if is_negative:
            drops = -drops

        return drops
