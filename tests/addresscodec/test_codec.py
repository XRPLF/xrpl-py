import unittest
import hashlib

from xrpl import addresscodec

class TestCodec(unittest.TestCase):
    def test_encode_and_decode(self):
        base58_string = 'rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN'
        hex_string = 'BA8E78626EE42C41B46D46C3048DF3A1C3C87072'
        encoded_hex = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode(encoded_hex, addresscodec.ACCOUNT_ID_PREFIX, 20)
        self.assertEqual(encode_result, base58_string)

        decode_result = addresscodec.decode(base58_string, len(addresscodec.ACCOUNT_ID_PREFIX))
        self.assertEqual(decode_result, encoded_hex)

        hex_string2 = '2decab42ca805119a9ba2ff305c9afa12f0b86a1'
        base58_string2 = 'rnBFvgZphmN39GWzUJeUitaP22Fr9be75H'
        encoded_hex2 = bytes.fromhex(hex_string2)

        encode_result2 = addresscodec.encode(encoded_hex2, addresscodec.ACCOUNT_ID_PREFIX, 20)
        self.assertEqual(encode_result2, base58_string2)

        decode_result2 = addresscodec.decode(base58_string2, len(addresscodec.ACCOUNT_ID_PREFIX))
        self.assertEqual(decode_result2, encoded_hex2)

    
    def test_encode_and_decode_longer_prefix(self):
        ed_seed = 'sEdTM1uX8pu2do5XvTnutH6HsouMaM2'
        decoded_seed = '4C3A1D213FBDFB14C7C28D609469B341'
        decoded_seed_bytes = bytes.fromhex(decoded_seed)

        encode_result = addresscodec.encode(decoded_seed_bytes, addresscodec.ED25519_SEED_PREFIX, 16)
        self.assertEqual(encode_result, ed_seed)

        decode_result = addresscodec.decode(ed_seed, len(addresscodec.ED25519_SEED_PREFIX))
        self.assertEqual(decode_result, decoded_seed_bytes)
    
    # account public key encode/decode tests

    def test_encode_account_public_key(self):
        hex_string = '023693F15967AE357D0327974AD46FE3C127113B1110D6044FD41E723689F81CC6'
        encoded_string = 'aB44YfzW24VDEJQ2UuLPV2PvqcPCSoLnL7y5M1EzhdW4LnK5xMS3'
        hex_string_bytes = bytes.fromhex(hex_string)

        result = addresscodec.encode_account_public_key(hex_string_bytes)
        self.assertEqual(result, encoded_string) 

        encode_result = addresscodec.encode_account_public_key(hex_string_bytes)
        self.assertEqual(encode_result, encoded_string)

        decode_result = addresscodec.decode_account_public_key(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
