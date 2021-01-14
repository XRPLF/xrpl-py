import unittest

from xrpl import addresscodec


class TestCodec(unittest.TestCase):
    def test_encode_and_decode(self):
        base58_string = "rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN"
        hex_string = "BA8E78626EE42C41B46D46C3048DF3A1C3C87072"
        encoded_hex = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode(
            encoded_hex,
            addresscodec.CLASSIC_ADDRESS_PREFIX,
            addresscodec.CLASSIC_ADDRESS_LENGTH,
        )
        self.assertEqual(encode_result, base58_string)

        decode_result = addresscodec.decode(
            base58_string, len(addresscodec.CLASSIC_ADDRESS_PREFIX)
        )
        self.assertEqual(decode_result, encoded_hex)

        hex_string2 = "2decab42ca805119a9ba2ff305c9afa12f0b86a1"
        base58_string2 = "rnBFvgZphmN39GWzUJeUitaP22Fr9be75H"
        encoded_hex2 = bytes.fromhex(hex_string2)

        encode_result2 = addresscodec.encode(
            encoded_hex2,
            addresscodec.CLASSIC_ADDRESS_PREFIX,
            addresscodec.CLASSIC_ADDRESS_LENGTH,
        )
        self.assertEqual(encode_result2, base58_string2)

        decode_result2 = addresscodec.decode(
            base58_string2, len(addresscodec.CLASSIC_ADDRESS_PREFIX)
        )
        self.assertEqual(decode_result2, encoded_hex2)

    def test_encode_and_decode_longer_prefix(self):
        ed_seed = "sEdTM1uX8pu2do5XvTnutH6HsouMaM2"
        decoded_seed = "4C3A1D213FBDFB14C7C28D609469B341"
        decoded_seed_bytes = bytes.fromhex(decoded_seed)

        encode_result = addresscodec.encode(
            decoded_seed_bytes, addresscodec.ED25519_SEED_PREFIX, 16
        )
        self.assertEqual(encode_result, ed_seed)

        decode_result = addresscodec.decode(
            ed_seed, len(addresscodec.ED25519_SEED_PREFIX)
        )
        self.assertEqual(decode_result, decoded_seed_bytes)

    # seed tests

    def test_seed_encode_decode_secp256k1(self):
        hex_string = "CF2DE378FBDD7E2EE87D486DFB5A7BFF"
        encoded_string = "sn259rEFXrQrWyx3Q7XneWcwV6dfL"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_seed(
            hex_string_bytes, addresscodec.SECP256K1
        )
        self.assertEqual(encode_result, encoded_string)

        decode_result, encoding_type = addresscodec.decode_seed(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
        self.assertEqual(encoding_type, addresscodec.SECP256K1)

    def test_seed_encode_decode_secp256k1_low(self):
        hex_string = "00000000000000000000000000000000"
        encoded_string = "sp6JS7f14BuwFY8Mw6bTtLKWauoUs"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_seed(
            hex_string_bytes, addresscodec.SECP256K1
        )
        self.assertEqual(encode_result, encoded_string)

        decode_result, encoding_type = addresscodec.decode_seed(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
        self.assertEqual(encoding_type, addresscodec.SECP256K1)

    def test_seed_encode_decode_secp256k1_high(self):
        hex_string = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        encoded_string = "saGwBRReqUNKuWNLpUAq8i8NkXEPN"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_seed(
            hex_string_bytes, addresscodec.SECP256K1
        )
        self.assertEqual(encode_result, encoded_string)

        decode_result, encoding_type = addresscodec.decode_seed(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
        self.assertEqual(encoding_type, addresscodec.SECP256K1)

    def test_seed_encode_decode_ed25519(self):
        hex_string = "4C3A1D213FBDFB14C7C28D609469B341"
        encoded_string = "sEdTM1uX8pu2do5XvTnutH6HsouMaM2"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_seed(hex_string_bytes, addresscodec.ED25519)
        self.assertEqual(encode_result, encoded_string)

        decode_result, encoding_type = addresscodec.decode_seed(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
        self.assertEqual(encoding_type, addresscodec.ED25519)

    def test_seed_encode_decode_ed25519_low(self):
        hex_string = "00000000000000000000000000000000"
        encoded_string = "sEdSJHS4oiAdz7w2X2ni1gFiqtbJHqE"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_seed(hex_string_bytes, addresscodec.ED25519)
        self.assertEqual(encode_result, encoded_string)

        decode_result, encoding_type = addresscodec.decode_seed(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
        self.assertEqual(encoding_type, addresscodec.ED25519)

    def test_seed_encode_decode_ed25519_high(self):
        hex_string = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        encoded_string = "sEdV19BLfeQeKdEXyYA4NhjPJe6XBfG"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_seed(hex_string_bytes, addresscodec.ED25519)
        self.assertEqual(encode_result, encoded_string)

        decode_result, encoding_type = addresscodec.decode_seed(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
        self.assertEqual(encoding_type, addresscodec.ED25519)

    def test_seed_encode_decode_too_small(self):
        hex_string = "CF2DE378FBDD7E2EE87D486DFB5A7B"
        hex_string_bytes = bytes.fromhex(hex_string)

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.encode_seed,
            hex_string_bytes,
            addresscodec.SECP256K1,
        )

    def test_seed_encode_decode_too_big(self):
        hex_string = "CF2DE378FBDD7E2EE87D486DFB5A7BFFFF"
        hex_string_bytes = bytes.fromhex(hex_string)

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.encode_seed,
            hex_string_bytes,
            addresscodec.SECP256K1,
        )

    # classic_address tests

    def test_classic_address_encode_decode(self):
        hex_string = "BA8E78626EE42C41B46D46C3048DF3A1C3C87072"
        encoded_string = "rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_classic_address(hex_string_bytes)
        self.assertEqual(encode_result, encoded_string)

        decode_result = addresscodec.decode_classic_address(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)

    def test_encode_classic_address_bad_length(self):
        hex_string = "ABCDEF"
        hex_string_bytes = bytes.fromhex(hex_string)

        self.assertRaises(
            addresscodec.XRPLAddressCodecException,
            addresscodec.encode_classic_address,
            hex_string_bytes,
        )

    # node_public_key test

    def test_node_public_key_encode_decode(self):
        hex_string = (
            "0388E5BA87A000CB807240DF8C848EB0B5FFA5C8E5A521BC8E105C0F0A44217828"
        )
        encoded_string = "n9MXXueo837zYH36DvMc13BwHcqtfAWNJY5czWVbp7uYTj7x17TH"
        hex_string_bytes = bytes.fromhex(hex_string)

        encode_result = addresscodec.encode_node_public_key(hex_string_bytes)
        self.assertEqual(encode_result, encoded_string)

        decode_result = addresscodec.decode_node_public_key(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)

    # account public key test

    def test_encode_account_public_key(self):
        hex_string = (
            "023693F15967AE357D0327974AD46FE3C127113B1110D6044FD41E723689F81CC6"
        )
        encoded_string = "aB44YfzW24VDEJQ2UuLPV2PvqcPCSoLnL7y5M1EzhdW4LnK5xMS3"
        hex_string_bytes = bytes.fromhex(hex_string)

        result = addresscodec.encode_account_public_key(hex_string_bytes)
        self.assertEqual(result, encoded_string)

        encode_result = addresscodec.encode_account_public_key(hex_string_bytes)
        self.assertEqual(encode_result, encoded_string)

        decode_result = addresscodec.decode_account_public_key(encoded_string)
        self.assertEqual(decode_result, hex_string_bytes)
