import unittest
import hashlib

from xrpl import addresscodec

class TestCodec(unittest.TestCase):
    def test_encode(self):
        base58_string = 'rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN'
        hex_string = 'BA8E78626EE42C41B46D46C3048DF3A1C3C87072'
        encoded_hex = bytes.fromhex(hex_string)

        result = addresscodec.encode(encoded_hex, [addresscodec.ACCOUNT_ID], 20)
        self.assertEqual(result, base58_string)
    
    def test_encode2(self):
        pubkey_hex = '2decab42ca805119a9ba2ff305c9afa12f0b86a1'
        base58_string = 'rnBFvgZphmN39GWzUJeUitaP22Fr9be75H'
        encoded_hex = bytes.fromhex(pubkey_hex)

        result = addresscodec.encode(encoded_hex, [addresscodec.ACCOUNT_ID], 20)
        self.assertEqual(result, base58_string)