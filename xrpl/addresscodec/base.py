import base58
from .exceptions import XRPLAddressCodecException
from .utils import XRPL_ALPHABET

MAX_32_BIT_UNSIGNED_INT = 4294967295

PREFIX_BYTES_MAIN = bytes([0x05, 0x44]) # 5, 68
PREFIX_BYTES_TEST = bytes([0x04, 0x93]) # 4, 147

def encode_xaddress(account_id, tag, test):
    if len(account_id) != 20:
        raise XRPLAddressCodecException('Account ID must be 20 bytes')
    
    if tag is not None and tag > MAX_32_BIT_UNSIGNED_INT:
        raise XRPLAddressCodecException('Invalid tag')

    flag = tag is not None
    if tag is None:
        tag = 0
    
    
    bytestring = PREFIX_BYTES_TEST if test else PREFIX_BYTES_MAIN
    bytestring += account_id
    encoded_tag = bytes([flag, tag & 0xff, tag >> 8 & 0xff, tag >> 16 & 0xff, tag >> 24 & 0xff, 0, 0, 0, 0])
    bytestring += encoded_tag

    return base58.b58encode_check(bytestring, alphabet=XRPL_ALPHABET).decode("utf-8")