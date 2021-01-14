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

def decode_xaddress(xaddress):
    decoded = base58.b58decode_check(xaddress)
    is_test = _is_test_address(decoded)
    classic_address = decoded[2:22]
    tag = _get_tag_from_buffer(decoded)

    return (classic_address, tag, is_test)

def _is_test_address(buffer):
    decoded_prefix = buffer[:2]
    if PREFIX_BYTES_MAIN == decoded_prefix:
        return False
    elif PREFIX_BYTES_TEST == decoded_prefix:
        return True
    else:
        raise XRPLAddressCodecException('Invalid X-Address: bad prefix')

def _get_tag_from_buffer(buffer):
    flag = buffer[22]
    if flag >= 2:
        raise XRPLAddressCodecException('Unsupported X-Address')
    if flag == 1: # Little-endian to big-endian
        return buffer[23] + buffer[24] * 0x100 + buffer[25] * 0x10000 + buffer[26] * 0x1000000
    if flag != 0:
        raise XRPLAddressCodecException('Flag must be zero to indicate no tag')
    if bytes.fromhex('0000000000000000') != buffer[23:23+8]:
        raise XRPLAddressCodecException('Remaining bytes must be zero')
    return None