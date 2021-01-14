import base58
from .codec import decode_classic_address
from .exceptions import XRPLAddressCodecException
from .utils import XRPL_ALPHABET

MAX_32_BIT_UNSIGNED_INT = 4294967295

PREFIX_BYTES_MAIN = bytes([0x05, 0x44])  # 5, 68
PREFIX_BYTES_TEST = bytes([0x04, 0x93])  # 4, 147


def encode_xaddress(classic_address_bytes, tag, test):
    """
    classic_address_bytes: bytes, representing the classic address
    tag: int, the destination tag
    test: boolean, whether it is the test network or not (aka the main network)

    Returns the X-address representation of the data
    """
    if len(classic_address_bytes) != 20:
        raise XRPLAddressCodecException("Account ID must be 20 bytes")

    if tag is not None and tag > MAX_32_BIT_UNSIGNED_INT:
        raise XRPLAddressCodecException("Invalid tag")

    flag = tag is not None
    if tag is None:
        tag = 0

    bytestring = PREFIX_BYTES_TEST if test else PREFIX_BYTES_MAIN
    bytestring += classic_address_bytes
    encoded_tag = bytes(
        [
            flag,
            tag & 0xFF,
            tag >> 8 & 0xFF,
            tag >> 16 & 0xFF,
            tag >> 24 & 0xFF,
            0,
            0,
            0,
            0,
        ]
    )
    bytestring += encoded_tag

    return base58.b58encode_check(bytestring, alphabet=XRPL_ALPHABET).decode("utf-8")


def classic_address_to_xaddress(classic_address, tag, test):
    """
    classic_address: string, the base58 encoding of the classic address
    tag: int, the destination tag
    test: boolean, whether it is the test network or not (aka the main network)

    Returns the X-address representation of the data
    """
    address_bytes = decode_classic_address(classic_address)
    return encode_xaddress(address_bytes, tag, test)
