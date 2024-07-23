"""Conversions between integer and hexadecimal types."""


def int_to_hex(input: int) -> int:
    """
    Convert an integer to a hexadecimal string and remove the '0x' prefix.
    XRPL uses hex strings as inputs in fields like `MaximumAmount`
    in the `MPTokenIssuanceCreate` transaction.

    Args:
        input: integer to convert

    Returns:
        Input encoded as a hex string.
    """
    return hex(input)[2:]


def hex_to_int(input: int) -> int:
    """
    Convert a hexadecimal string into an integer.
    XRPL uses hex strings as inputs in fields like `MaximumAmount`
    in the `MPTokenIssuanceCreate` transaction.

    Args:
        input: hex-encoded string to convert

    Returns:
        Input encoded as a human-readable string.
    """
    return int(input, 16)
