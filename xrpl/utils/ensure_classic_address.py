"""Classic address helper utils."""

from xrpl.constants import XRPLException
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address


def ensure_classic_address(account: str) -> str:
    """
    If an address is an X-Address, converts it to a classic address.

    Args:
        account: A classic address or X-address.

    Returns:
        The account's classic address

    Raises:
        XRPLException: if the X-Address has an associated tag.
    """
    if is_valid_xaddress(account):
        classic_address, tag, _ = xaddress_to_classic_address(account)

        """
        Except for special cases, X-addresses used for requests must not
        have an embedded tag. In other words, `tag` should be None.
        """
        if tag is not None:
            raise XRPLException(
                "This command does not support the use of a tag. Use "
                "an address without a tag"
            )

        return classic_address

    return account
