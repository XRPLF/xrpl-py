"""Defines how to serialize and deserialize an amount."""
from decimal import Decimal

from xrpl.binary_codec.types.serialized_type import SerializedType

# Constants for validating amounts.
# JS Constants
_MIN_IOU_EXPONENT = -96
_MAX_IOU_EXPONENT = 80
_MAX_IOU_PRECISION = 16
# MAX_DROPS = new Decimal("1e17");
# MIN_XRP = new Decimal("1e-6");

# other JAVA constants:
_DEFAULT_AMOUNT_HEX = "4000000000000000"
_ZERO_CURRENCY_AMOUNT_HEX = "8000000000000000"
_NATIVE_AMOUNT_BYTE_LENGTH = 8
_CURRENCY_AMOUNT_BYTE_LENGTH = 48


"""
/**
 * decimal.js configuration for Amount IOUs
 */
Decimal.config({
  toExpPos: MAX_IOU_EXPONENT + MAX_IOU_PRECISION,
  toExpNeg: MIN_IOU_EXPONENT - MAX_IOU_PRECISION,
});

/**
 * Interface for JSON objects that represent amounts
 */
interface AmountObject extends JsonObject {
  value: string;
  currency: string;
  issuer: string;
}

/**
 * Type guard for AmountObject
 */
function isAmountObject(arg): arg is AmountObject {
  const keys = Object.keys(arg).sort();
  return (
    keys.length === 3 &&
    keys[0] === "currency" &&
    keys[1] === "issuer" &&
    keys[2] === "value"
  );
}
"""


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

    # TODO: when it's all writ: are all these docstrings correct?
    def assert_xrp_is_valid(self, xrp_value: str) -> None:
        """
        Validates the format of an XRP amount.
        Raises if value is invalid.

        :param xrp_value: A string representing an integer number of drops of XRP.
        """
        # contains no decimal point

        # const decimal = new Decimal(amount);
        # is this check necessary?
        #     if (!decimal.isZero()) {
        #       if (decimal.lt(MIN_XRP) || decimal.gt(MAX_DROPS)) {
        #         throw new Error(`${amount.toString()} is an illegal amount`);
        #       }
        #
        pass

    def assert_iou_is_valid(self, issued_currency_value: Decimal) -> None:
        """
        Validates the format of an issued currency amount value.
        Raises if value is invalid.

        :param issued_currency_value: A Decimal object representing the "value"
                                        field of an issued currency amount.
        """
        # if (!decimal.equals(BigDecimal.ZERO)) {
        #   int p = decimal.precision();
        #   int e = MathUtils.getExponent(decimal);
        #   if (p > MAX_IOU_PRECISION ||
        #       e > MAX_IOU_EXPONENT ||
        #       e < MIN_IOU_EXPONENT
        #   ) {
        #     throw new Error("Decimal precision out of range");
        #   }
        #   verifyNoDecimal(decimal);
        # }
        pass

    def verify_no_decimal(self, decimal: Decimal) -> None:
        """
        Ensure that the value after being multiplied by the exponent
        does not contain a decimal.

        :param decimal: A Decimal object.
        """
        # BigDecimal exponent =
        #               new BigDecimal("1e" + -(MathUtils.getExponent(decimal) - 15));
        # String integerNumberString = decimal.multiply(exponent).toPlainString();
        # if (integerNumberString.indexOf(".") > 0) {
        #     throw new Error("Decimal place found in integerNumberString");
        # }
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
