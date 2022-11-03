from unittest import TestCase

from xrpl.constants import CryptoAlgorithm
from xrpl.wallet.main import Wallet

classic_address_prefix = "r"
ed25519_key_prefix = "ED"
secp256k1_private_key_prefix = "00"

# why do we even allow specification of seed and algorithm? seed should be enough
# to determine algorithm?
# why do we allow seed to result in multiple addresses depending on algorithm?
# should from_seed have default algorithm

# yes, default from_seed and from_entropy
# why doesn't my from_seed defaulted make same as xrpl.js on same seed (regular pair)
# does xrpl.js even allow specifying algorithm in derivekeypair? look into it.
# passed into opts of derive keypair but then what

regular_key_pair_constants = {
    "master_address": "rUAi7pipxGpYfPNg3LtPcf2ApiS8aw9A93",
    "seed": "sh8i92YRnEjJy3fpFkL8txQSCVo79",
    "public_key": "03AEEFE1E8ED4BBC009DE996AC03A8C6B5713B1554794056C66E5B8D1753C7DD0E",
    "private_key": "004265A28F3E18340A490421D47B2EB8DBC2C0BF2C24CEFEA971B61CED2CABD233",
}

seed_constants = {
    "seed": "ssL9dv2W5RK8L3tuzQxYY6EaZhSxW",
    "ed25519_public_key": "ED16FD02F7A7E52B6ACB35F8A4D7013DC94755951629DB6611483590AC0E9FC6D5",  # noqa:E501
    "ed25519_private_key": "ED713A8C3171A3D8F69FE9526D9243834B3A30BF893B1EBC1824B1D96F18B44DCF",  # noqa:E501
    "ed25519_classic_address": "rPxLJ2GumwfLk3z9njmmpo8nAX7sfZYptV",
    "secp256k1_public_key": "030E58CDD076E798C84755590AAF6237CA8FAE821070A59F648B517A30DC6F589D",  # noqa:E501
    "secp256k1_private_key": "00141BA006D3363D2FB2785E8DF4E44D3A49908780CB4FB51F6D217C08C021429F",  # noqa:E501
    "secp256k1_classic_address": "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc",
}

entropy_constants = {
    "entropy": "0000000000000000",
    "ed25519_public_key": "ED4AF1C789A6F18C2C79779EC569C9FE7980390EF8257DCE5290744B929ABF3FFB",  # noqa:E501
    "ed25519_private_key": "ED56D01C4D1A698E26AC99EEFDD77B9E98F1B909B407282830E8DFFC18FB99F215",  # noqa:E501
    "secp256k1_public_key": "ED4AF1C789A6F18C2C79779EC569C9FE7980390EF8257DCE5290744B929ABF3FFB",  # noqa:E501
    "secp256k1_private_key": "ED4AF1C789A6F18C2C79779EC569C9FE7980390EF8257DCE5290744B929ABF3FFB",  # noqa:E501
    "classic_address": "r4qwiunCmy3LLVGQGNQmmEbHVaCiuoo5sk",
}


class TestWalletMain(TestCase):
    def test_constructor_using_defaults(self):
        wallet = Wallet()

        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.private_key, str)
        self.assertIsInstance(wallet.classic_address, str)
        self.assertIsInstance(wallet.seed, str)
        self.assertIsInstance(wallet.sequence, int)
        self.assertTrue(wallet.public_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.private_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    def test_constructor_using_seed(self):
        # results in secp256k1 wallet variables because seed is inferred as secp256k1
        wallet = Wallet(seed_constants["seed"])

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_create_using_default_algorithm(self):
        wallet = Wallet.create()

        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.private_key, str)
        self.assertIsInstance(wallet.classic_address, str)
        self.assertIsInstance(wallet.seed, str)
        self.assertIsInstance(wallet.sequence, int)
        self.assertTrue(wallet.public_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.private_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    def test_create_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.create(CryptoAlgorithm.SECP256K1)

        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.private_key, str)
        self.assertIsInstance(wallet.classic_address, str)
        self.assertIsInstance(wallet.seed, str)
        self.assertIsInstance(wallet.sequence, int)
        self.assertTrue(wallet.private_key.startswith(secp256k1_private_key_prefix))
        self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    def test_from_public_private(self):
        wallet = Wallet.from_public_private_keys(
            seed_constants["secp256k1_public_key"],
            seed_constants["secp256k1_private_key"],
        )

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_from_public_private_using_regular_key_pair(self):
        wallet = Wallet.from_public_private_keys(
            regular_key_pair_constants["public_key"],
            regular_key_pair_constants["private_key"],
            regular_key_pair_constants["master_address"],
        )

        self.assertEqual(wallet.public_key, regular_key_pair_constants["public_key"])
        self.assertEqual(wallet.private_key, regular_key_pair_constants["private_key"])
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_seed_using_default_algorithm(self):
        # seed is inferred as secp256k1 but default algorithm is ed25519
        # should from_seed even have a default algorithm?
        wallet = Wallet.from_seed(seed_constants["seed"])

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_from_seed_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_seed(
            seed_constants["seed"], crypto_algorithm=CryptoAlgorithm.SECP256K1
        )

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_from_seed_using_algorithm_ed25519(self):
        wallet = Wallet.from_seed(
            seed_constants["seed"], crypto_algorithm=CryptoAlgorithm.ED25519
        )

        self.assertEqual(wallet.public_key, seed_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["ed25519_classic_address"]
        )

    def test_from_seed_using_regular_key_pair(self):
        # seed is inferred as secp256k1 but default algorithm is ed25519
        # should from_seed even have a default algorithm?
        wallet = Wallet.from_seed(
            regular_key_pair_constants["seed"],
            regular_key_pair_constants["master_address"],
        )

        self.assertEqual(wallet.public_key, regular_key_pair_constants["public_key"])
        self.assertEqual(wallet.private_key, regular_key_pair_constants["private_key"])
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    # def test_from_secret_using_default_algorithm(self):
    #     pass

    # def test_from_secret_using_algorithm_ecdsa_secp256k1(self):
    #     pass

    # def test_from_secret_using_algorithm_ed25519(self):
    #     pass

    # def test_from_secret_using_regular_key_pair(self):
    #     pass

    def test_from_entropy_using_default_algorithm(self):
        wallet = Wallet.from_entropy(entropy_constants["entropy"])

        self.assertEqual(wallet.public_key, entropy_constants["public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["private_key"])
        self.assertEqual(wallet.classic_address, entropy_constants["classic_address"])

    # def test_from_entropy_using_algorithm_ecdsa_secp256k1(self):
    #     # pass  # fails because not ED25519 result
    #     wallet = Wallet.from_entropy(
    #         entropy_constants["entropy"], crypto_algorithm=CryptoAlgorithm.SECP256K1
    #     )

    #     self.assertEqual(wallet.public_key, entropy_constants["public_key"])
    #     self.assertEqual(wallet.private_key, entropy_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, entropy_constants["classic_address"])

    # def test_from_entropy_using_algorithm_ed25519(self):
    #     wallet = Wallet.from_entropy(
    #         entropy_constants["entropy"], crypto_algorithm=CryptoAlgorithm.ED25519
    #     )

    #     self.assertEqual(wallet.public_key, entropy_constants["public_key"])
    #     self.assertEqual(wallet.private_key, entropy_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, entropy_constants["classic_address"])

    # def test_from_entropy_using_regular_key_pair(self):
    #     wallet = Wallet.from_entropy(
    #         entropy_constants["entropy"], regular_key_pair_constants["master_address"]
    #     )

    #     self.assertEqual(wallet.public_key, entropy_constants["public_key"])
    #     self.assertEqual(wallet.private_key, entropy_constants["private_key"])
    #     self.assertEqual(
    #         wallet.classic_address, regular_key_pair_constants["master_address"]
    #     )

    # def test_get_xaddress_when_test_is_true(self):
    #     pass

    # def test_get_xaddress_when_test_is_false(self):
    #     pass

    # def test_get_xaddress_when_test_is_not_provided(self):
    #     pass

    # def test_address_alias(self):
    #     wallet = Wallet()
    #     self.assertEqual(wallet.address, wallet.classic_address)
    #     wallet.address = "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc"
    #     self.assertEqual(wallet.address, wallet.classic_address)
    #     wallet.classic_address = "r4qwiunCmy3LLVGQGNQmmEbHVaCiuoo5sk"
    #     self.assertEqual(wallet.address, wallet.classic_address)
