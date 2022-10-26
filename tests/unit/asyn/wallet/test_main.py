from unittest import TestCase

# from xrpl.constants import CryptoAlgorithm
from xrpl.wallet.main import Wallet

classic_address_prefix = "r"
ed25519_key_prefix = "ED"
secp256k1_private_key_prefix = "00"

regular_key_pair_constants = {
    "master_address": "rUAi7pipxGpYfPNg3LtPcf2ApiS8aw9A93",
    "seed": "sh8i92YRnEjJy3fpFkL8txQSCVo79",
    "public_key": "03AEEFE1E8ED4BBC009DE996AC03A8C6B5713B1554794056C66E5B8D1753C7DD0E",
    "private_key": "004265A28F3E18340A490421D47B2EB8DBC2C0BF2C24CEFEA971B61CED2CABD233",
}

seed_constants = {
    "seed": "ssL9dv2W5RK8L3tuzQxYY6EaZhSxW",
    "public_key": "030E58CDD076E798C84755590AAF6237CA8FAE821070A59F648B517A30DC6F589D",
    "private_key": "00141BA006D3363D2FB2785E8DF4E44D3A49908780CB4FB51F6D217C08C021429F",
    "classic_address": "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc",
}

entropy_constants = {
    "entropy": "0000000000000000",
    "public_key": "ED4AF1C789A6F18C2C79779EC569C9FE7980390EF8257DCE5290744B929ABF3FFB",
    "private_key": "ED56D01C4D1A698E26AC99EEFDD77B9E98F1B909B407282830E8DFFC18FB99F215",
    "classic_address": "r4qwiunCmy3LLVGQGNQmmEbHVaCiuoo5sk",
}


class TestWalletMain(TestCase):
    # def test_constructor_using_defaults(self):
    #     wallet = Wallet()

    #     self.assertIsInstance(wallet.public_key, str)
    #     self.assertIsInstance(wallet.private_key, str)
    #     self.assertIsInstance(wallet.classic_address, str)
    #     self.assertIsInstance(wallet.seed, str)
    #     self.assertIsInstance(wallet.sequence, int)
    #     self.assertTrue(wallet.public_key.startswith(ed25519_key_prefix))
    #     self.assertTrue(wallet.private_key.startswith(ed25519_key_prefix))
    #     self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    # def test_constructor_using_seed(self):
    #     wallet = Wallet(seed_constants["seed"])

    #     self.assertEqual(wallet.public_key, seed_constants["public_key"])
    #     self.assertEqual(wallet.private_key, seed_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_create_using_default_algorithm(self):
    #     wallet = Wallet.create()

    #     self.assertIsInstance(wallet.public_key, str)
    #     self.assertIsInstance(wallet.private_key, str)
    #     self.assertIsInstance(wallet.classic_address, str)
    #     self.assertIsInstance(wallet.seed, str)
    #     self.assertIsInstance(wallet.sequence, int)
    #     self.assertTrue(wallet.public_key.startswith(ed25519_key_prefix))
    #     self.assertTrue(wallet.private_key.startswith(ed25519_key_prefix))
    #     self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    # def test_create_using_algorithm_ecdsa_secp256k1(self):
    #     wallet = Wallet.create(crypto_algorithm=CryptoAlgorithm.SECP256K1)

    #     self.assertIsInstance(wallet.public_key, str)
    #     self.assertIsInstance(wallet.private_key, str)
    #     self.assertIsInstance(wallet.classic_address, str)
    #     self.assertIsInstance(wallet.seed, str)
    #     self.assertIsInstance(wallet.sequence, int)
    #     self.assertTrue(wallet.private_key.startswith(secp256k1_private_key_prefix))
    #     self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    # def test_from_public_private_using_default_algorithm(self):
    #     wallet = Wallet.from_public_private_keys(
    #         seed_constants["public_key"], seed_constants["private_key"]
    #     )

    #     self.assertEqual(wallet.public_key, seed_constants["public_key"])
    #     self.assertEqual(wallet.private_key, seed_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_from_public_private_using_algorithm_ecdsa_secp256k1(self):
    #     wallet = Wallet.from_public_private_keys(
    #         seed_constants["public_key"],
    #         seed_constants["private_key"],
    #         crypto_algorithm=CryptoAlgorithm.SECP256K1,
    #     )

    #     self.assertEqual(wallet.public_key, seed_constants["public_key"])
    #     self.assertEqual(wallet.private_key, seed_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_from_public_private_using_algorithm_ed25519(self):
    #     wallet = Wallet.from_public_private_keys(
    #         seed_constants["public_key"],
    #         seed_constants["private_key"],
    #         crypto_algorithm=CryptoAlgorithm.ED25519,
    #     )

    #     self.assertEqual(wallet.public_key, seed_constants["public_key"])
    #     self.assertEqual(wallet.private_key, seed_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_from_public_private_using_regular_key_pair(self):
    #     wallet = Wallet.from_public_private_keys(
    #         regular_key_pair_constants["public_key"],
    #         regular_key_pair_constants["private_key"],
    #         regular_key_pair_constants["master_address"],
    #     )

    #     self.assertEqual(wallet.public_key, regular_key_pair_constants["public_key"])
    # self.assertEqual(
    #     wallet.private_key,
    #     regular_key_pair_constants["private_key"]
    # )
    #     self.assertEqual(
    #         wallet.classic_address, regular_key_pair_constants["master_address"]
    #     )

    def test_from_seed_using_default_algorithm(self):
        wallet = Wallet.from_seed(seed_constants["seed"])

        self.assertEqual(wallet.public_key, seed_constants["public_key"])
        self.assertEqual(wallet.private_key, seed_constants["private_key"])
        self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_from_seed_using_algorithm_ecdsa_secp256k1(self):
    #     wallet = Wallet.from_seed(
    #         seed_constants["seed"], crypto_algorithm=CryptoAlgorithm.SECP256K1
    #     )

    #     self.assertEqual(wallet.public_key, seed_constants["public_key"])
    #     self.assertEqual(wallet.private_key, seed_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_from_seed_using_algorithm_ed25519(self):
    #     # pass  # doesn't work - might need ED version of public and private keys
    #     wallet = Wallet.from_seed(
    #         seed_constants["seed"], crypto_algorithm=CryptoAlgorithm.ED25519
    #     )

    #     self.assertEqual(wallet.public_key, seed_constants["public_key"])
    #     self.assertEqual(wallet.private_key, seed_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, seed_constants["classic_address"])

    # def test_from_seed_using_regular_key_pair(self):
    #     # pass  # fails if not SECP256K1
    #     wallet = Wallet.from_seed(
    #         regular_key_pair_constants["seed"],
    #         regular_key_pair_constants["master_address"],
    #     )

    #     self.assertEqual(wallet.public_key, regular_key_pair_constants["public_key"])
    # self.assertEqual(
    #     wallet.private_key,
    #     regular_key_pair_constants["private_key"]
    # )
    #     self.assertEqual(
    #         wallet.classic_address, regular_key_pair_constants["master_address"]
    #     )

    # def test_from_secret_using_default_algorithm(self):
    #     pass

    # def test_from_secret_using_algorithm_ecdsa_secp256k1(self):
    #     pass

    # def test_from_secret_using_algorithm_ed25519(self):
    #     pass

    # def test_from_secret_using_regular_key_pair(self):
    #     pass

    # def test_from_entropy_using_default_algorithm(self):
    #     wallet = Wallet.from_entropy(entropy_constants["entropy"])

    #     self.assertEqual(wallet.public_key, entropy_constants["public_key"])
    #     self.assertEqual(wallet.private_key, entropy_constants["private_key"])
    #     self.assertEqual(wallet.classic_address, entropy_constants["classic_address"])

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
