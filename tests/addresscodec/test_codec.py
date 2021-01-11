import unittest
import hashlib

from xrpl import addresscodec

class TestCodec(unittest.TestCase):
    def test_encode(self):
        base58_string = 'rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN'
        hex_string = 'BA8E78626EE42C41B46D46C3048DF3A1C3C87072'
        encoded_hex = bytes.fromhex(hex_string)

        result = addresscodec.encode(encoded_hex, addresscodec.ACCOUNT_ID_PREFIX, addresscodec.ACCOUNT_ID_LENGTH)
        self.assertEqual(result, base58_string)

        hex_string2 = '2decab42ca805119a9ba2ff305c9afa12f0b86a1'
        base58_string2 = 'rnBFvgZphmN39GWzUJeUitaP22Fr9be75H'
        encoded_hex2 = bytes.fromhex(hex_string2)

        result = addresscodec.encode(encoded_hex2, addresscodec.ACCOUNT_ID_PREFIX, addresscodec.ACCOUNT_ID_LENGTH)
        self.assertEqual(result, base58_string2)
    
    def test_encode_longer_prefix(self):
        ed_seed = 'sEdTM1uX8pu2do5XvTnutH6HsouMaM2'
        decoded_seed = '4C3A1D213FBDFB14C7C28D609469B341'
        decoded_seed_bytes = bytes.fromhex(decoded_seed)

        result = addresscodec.encode(decoded_seed_bytes, addresscodec.ED25519_SEED_PREFIX, 16)
        self.assertEqual(result, ed_seed)

    # encode_account_id tests

    def test_encode_account_id(self):
        hex_string = 'BA8E78626EE42C41B46D46C3048DF3A1C3C87072'
        encoded_string = 'rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN'
        hex_string_bytes = bytes.fromhex(hex_string)

        result = addresscodec.encode_account_id(hex_string_bytes)
        self.assertEqual(result, encoded_string)
    
    def test_encode_account_id_bad_length(self):
        hex_string = 'ABCDEF'
        hex_string_bytes = bytes.fromhex(hex_string)

        self.assertRaises(addresscodec.XRPLAddressCodecException, 
            addresscodec.encode_account_id, 
            hex_string_bytes
        )