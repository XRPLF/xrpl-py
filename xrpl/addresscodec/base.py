from .exceptions import XRPLAddressCodecException

MAX_32_BIT_UNSIGNED_INT = 4294967295

def encode_xaddress(account_id, tag, test):
    if len(account_id) != 20:
        raise XRPLAddressCodecException('Account ID must be 20 bytes')

