import unittest
import hashlib

from xrpl import addresscodec

class TestCodec(unittest.TestCase):
    def test_encode(self):
        base58_string = 'rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN'
        hex_string = 'BA8E78626EE42C41B46D46C3048DF3A1C3C87072'
        encoded_hex = bytes.fromhex(hex_string)

        result = addresscodec.encode(encoded_hex, addresscodec.ACCOUNT_ID_PREFIX, 20)
        self.assertEqual(result, base58_string)

        hex_string2 = '2decab42ca805119a9ba2ff305c9afa12f0b86a1'
        base58_string2 = 'rnBFvgZphmN39GWzUJeUitaP22Fr9be75H'
        encoded_hex2 = bytes.fromhex(hex_string2)

        result = addresscodec.encode(encoded_hex2, addresscodec.ACCOUNT_ID_PREFIX, 20)
        self.assertEqual(result, base58_string2)
    
    def test_encode_longer_prefix(self):
        ed_seed = 'sEdTM1uX8pu2do5XvTnutH6HsouMaM2'
        decoded_seed = '4C3A1D213FBDFB14C7C28D609469B341'
        decoded_seed_bytes = bytes.fromhex(decoded_seed)

        result = addresscodec.encode(decoded_seed_bytes, addresscodec.ED25519_SEED_PREFIX, 16)
        self.assertEqual(result, ed_seed)
    
    # encode_seed tests

    def test_encode_seed_secp256k1(self):
        result = addresscodec.encode_seed(bytes.fromhex('CF2DE378FBDD7E2EE87D486DFB5A7BFF'), 'secp256k1')
        self.assertEqual(result, 'sn259rEFXrQrWyx3Q7XneWcwV6dfL')

    def test_encode_seed_secp256k1_low(self):
        result = addresscodec.encode_seed(bytes.fromhex('00000000000000000000000000000000'), 'secp256k1')
        self.assertEqual(result, 'sp6JS7f14BuwFY8Mw6bTtLKWauoUs')

    def test_encode_seed_secp256k1_high(self):
        result = addresscodec.encode_seed(bytes.fromhex('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'), 'secp256k1')
        self.assertEqual(result, 'saGwBRReqUNKuWNLpUAq8i8NkXEPN')

    def test_encode_seed_ed25519(self):
        result = addresscodec.encode_seed(bytes.fromhex('4C3A1D213FBDFB14C7C28D609469B341'), 'ed25519')
        self.assertEqual(result, 'sEdTM1uX8pu2do5XvTnutH6HsouMaM2')

    def test_encode_seed_ed25519_low(self):
        result = addresscodec.encode_seed(bytes.fromhex('00000000000000000000000000000000'), 'ed25519')
        self.assertEqual(result, 'sEdSJHS4oiAdz7w2X2ni1gFiqtbJHqE')

    def test_encode_seed_ed25519_high(self):
        result = addresscodec.encode_seed(bytes.fromhex('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'), 'ed25519')
        self.assertEqual(result, 'sEdV19BLfeQeKdEXyYA4NhjPJe6XBfG')

    def test_encode_seed_too_small(self):
        self.assertRaises(addresscodec.XRPLAddressCodecException, 
            addresscodec.encode_seed, 
            bytes.fromhex('CF2DE378FBDD7E2EE87D486DFB5A7B'), 
            'secp256k1'
        )

    def test_encode_too_big(self):
        self.assertRaises(addresscodec.XRPLAddressCodecException, 
            addresscodec.encode_seed, 
            bytes.fromhex('CF2DE378FBDD7E2EE87D486DFB5A7BFFFF')
            , 'secp256k1'
        )