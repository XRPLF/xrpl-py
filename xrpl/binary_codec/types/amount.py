"""Defines how to serialize and deserialize an amount field."""
from decimal import Context, Decimal, getcontext, setcontext
from typing import Dict

from xrpl.binary_codec.exceptions import XRPLBinaryCodecException

# from xrpl.binary_codec.types.account_id import AccountID
# from xrpl.binary_codec.types.currency import Currency
from xrpl.binary_codec.types.serialized_type import SerializedType

# Constants for validating amounts.
_MIN_IOU_EXPONENT = -96
_MAX_IOU_EXPONENT = 80
_MAX_IOU_PRECISION = 16

# Configure Decimal
setcontext(
    Context(prec=_MAX_IOU_PRECISION, Emax=_MAX_IOU_EXPONENT, Emin=_MIN_IOU_EXPONENT)
)

_MAX_DROPS = Decimal("1e17")
_MIN_XRP = Decimal("1e-6")

# other constants:
_DEFAULT_AMOUNT_HEX = "4000000000000000"
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
    """Defines how to serialize and deserialize an amount."""

    def from_value(self, value):
        """

        :param value:
        :return:
        """
        # is the incoming value a string?
        # self.assert_xrp_is_valid(value)
        # represent and write the number as bytes to this buffer
        # some OR situation with 0x40...
        # return Amount object with this buffer

        # is the incoming value a dictionary?
        # does the dictionary have keys ["currency", "issuer", "value"]?
        # self.assert_iou_is_valid(value)
        # is it the special zero case?
        # write the 0x800... situation
        # else:
        # set up the amount, currency, and issuer bytes
        # write to buffer
        # return Amount object with this buffer
        # raise an error if it's not a string or correct dict

    def from_parser(self, parser):
        """Construct an Amount from an existing BinaryParser."""
        pass

    # this one exists only in JS not JAVA ... ?
    def to_json(self):
        """Construct a JSON object representing this Amount."""
        pass

    def is_native(self) -> bool:
        """Returns True if this amount is a native XRP amount."""
        # 1st bit in 1st byte is set to 0 for native XRP
        # return (toBytes()[0] & 0x80) == 0
        pass

    def is_positive(self) -> bool:
        """Returns True if 2nd bit in 1st byte is set to 1 (positive amount)."""
        # return (toBytes()[0] & 0x40) > 0

    # def get_amount_bytes(self):
    #     pass
