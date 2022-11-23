from unittest import TestCase

from xrpl.constants import CryptoAlgorithm
from xrpl.wallet.main import Wallet

classic_address_prefix = "r"
ed25519_key_prefix = "ED"
secp256k1_private_key_prefix = "00"

regular_key_pair_constants = {
    "master_address": "rUAi7pipxGpYfPNg3LtPcf2ApiS8aw9A93",
    "seed": "sh8i92YRnEjJy3fpFkL8txQSCVo79",
    "ed25519_public_key": "ED848AB5972C2D7885DBF188EAF1DC24C3EE8064E41C13AAFF3B731494B9C81990",  # noqa:E501
    "ed25519_private_key": "ED14CAA44B431CEE77F13139BFDE59F63CBEBCFF37C6F0F4AC6F05620A5EDBE33C",  # noqa:E501
    "secp256k1_public_key": "03AEEFE1E8ED4BBC009DE996AC03A8C6B5713B1554794056C66E5B8D1753C7DD0E",  # noqa:E501
    "secp256k1_private_key": "004265A28F3E18340A490421D47B2EB8DBC2C0BF2C24CEFEA971B61CED2CABD233",  # noqa:E501
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
    "ed25519_classic_address": "r4qwiunCmy3LLVGQGNQmmEbHVaCiuoo5sk",
    "secp256k1_public_key": "032632F887B83B32EE74A137C870C62DA776195ED2B106622B1DE5F3EAAF932CBB",  # noqa:E501
    "secp256k1_private_key": "00ED3FED5C377CF7014467AECA2DE76E42044C231AF4E5E3C00A5F8704F49F5B2D",  # noqa:E501
    "secp256k1_classic_address": "rDYKpeyzBvdut96cC9SU7wQUdMtJqEdrgn",
}

xaddress_constants = {
    "tag": 1337,
    "mainnet_xaddress": "X7gJ5YK8abHf2eTPWPFHAAot8Knck11QGqmQ7a6a3Z8PJvk",
    "testnet_xaddress": "T7bq3e7kxYq9pwDz8UZhqAZoEkcRGTXSNr5immvcj3DYRaV",
}
xaddress_wallet = Wallet(
    "030E58CDD076E798C84755590AAF6237CA8FAE821070A59F648B517A30DC6F589D",
    "00141BA006D3363D2FB2785E8DF4E44D3A49908780CB4FB51F6D217C08C021429F",
)


class TestWalletMain(TestCase):
    def test_constructor(self):
        wallet = Wallet(
            seed_constants["secp256k1_public_key"],
            seed_constants["secp256k1_private_key"],
            seed=seed_constants["seed"],
        )

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_constructor_using_regular_key_pair(self):
        wallet = Wallet(
            regular_key_pair_constants["secp256k1_public_key"],
            regular_key_pair_constants["secp256k1_private_key"],
            master_address=regular_key_pair_constants["master_address"],
            seed=regular_key_pair_constants["seed"],
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["secp256k1_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["secp256k1_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )
        self.assertEqual(wallet.seed, regular_key_pair_constants["seed"])

    def test_generate_using_default_algorithm(self):
        wallet = Wallet.generate()

        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.private_key, str)
        self.assertIsInstance(wallet.classic_address, str)
        self.assertIsInstance(wallet.address, str)
        self.assertIsInstance(wallet.seed, str)
        self.assertTrue(wallet.public_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.private_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    def test_generate_using_algorithm_ed25519(self):
        wallet = Wallet.generate()

        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.private_key, str)
        self.assertIsInstance(wallet.classic_address, str)
        self.assertIsInstance(wallet.address, str)
        self.assertIsInstance(wallet.seed, str)
        self.assertTrue(wallet.public_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.private_key.startswith(ed25519_key_prefix))
        self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    def test_generate_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.generate(CryptoAlgorithm.SECP256K1)

        self.assertIsInstance(wallet.public_key, str)
        self.assertIsInstance(wallet.private_key, str)
        self.assertIsInstance(wallet.classic_address, str)
        self.assertIsInstance(wallet.address, str)
        self.assertIsInstance(wallet.seed, str)
        self.assertTrue(wallet.private_key.startswith(secp256k1_private_key_prefix))
        self.assertTrue(wallet.classic_address.startswith(classic_address_prefix))

    def test_from_seed_using_default_algorithm(self):
        wallet = Wallet.from_seed(seed_constants["seed"])

        self.assertEqual(wallet.public_key, seed_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["ed25519_classic_address"]
        )

    def test_from_seed_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_seed(
            seed_constants["seed"], algorithm=CryptoAlgorithm.SECP256K1
        )

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_from_seed_using_algorithm_ed25519(self):
        wallet = Wallet.from_seed(
            seed_constants["seed"], algorithm=CryptoAlgorithm.ED25519
        )

        self.assertEqual(wallet.public_key, seed_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["ed25519_classic_address"]
        )

    def test_from_seed_using_regular_key_pair_using_no_algorithm(self):
        wallet = Wallet.from_seed(
            regular_key_pair_constants["seed"],
            master_address=regular_key_pair_constants["master_address"],
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["ed25519_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["ed25519_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_seed_using_regular_key_pair_using_algorithm_ed25519(self):
        wallet = Wallet.from_seed(
            regular_key_pair_constants["seed"],
            master_address=regular_key_pair_constants["master_address"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["ed25519_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["ed25519_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_seed_using_regular_key_pair_using_algorithm_edcsa_secp256k1(self):
        wallet = Wallet.from_seed(
            regular_key_pair_constants["seed"],
            master_address=regular_key_pair_constants["master_address"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["secp256k1_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["secp256k1_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_secret_using_default_algorithm(self):
        wallet = Wallet.from_secret(seed_constants["seed"])

        self.assertEqual(wallet.public_key, seed_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["ed25519_classic_address"]
        )

    def test_from_secret_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_secret(
            seed_constants["seed"], algorithm=CryptoAlgorithm.SECP256K1
        )

        self.assertEqual(wallet.public_key, seed_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["secp256k1_classic_address"]
        )

    def test_from_secret_using_algorithm_ed25519(self):
        wallet = Wallet.from_secret(
            seed_constants["seed"], algorithm=CryptoAlgorithm.ED25519
        )

        self.assertEqual(wallet.public_key, seed_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, seed_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, seed_constants["ed25519_classic_address"]
        )

    def test_from_secret_using_regular_key_pair_using_no_algorithm(self):
        wallet = Wallet.from_secret(
            regular_key_pair_constants["seed"],
            master_address=regular_key_pair_constants["master_address"],
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["ed25519_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["ed25519_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_secret_using_regular_key_pair_using_algorithm_ed25519(self):
        wallet = Wallet.from_secret(
            regular_key_pair_constants["seed"],
            master_address=regular_key_pair_constants["master_address"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["ed25519_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["ed25519_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_secret_using_regular_key_pair_using_algorithm_edcsa_secp256k1(self):
        wallet = Wallet.from_secret(
            regular_key_pair_constants["seed"],
            master_address=regular_key_pair_constants["master_address"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        self.assertEqual(
            wallet.public_key, regular_key_pair_constants["secp256k1_public_key"]
        )
        self.assertEqual(
            wallet.private_key, regular_key_pair_constants["secp256k1_private_key"]
        )
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_entropy_using_default_algorithm(self):
        wallet = Wallet.from_entropy(entropy_constants["entropy"])

        self.assertEqual(wallet.public_key, entropy_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, entropy_constants["ed25519_classic_address"]
        )

    def test_from_entropy_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_entropy(
            entropy_constants["entropy"], algorithm=CryptoAlgorithm.SECP256K1
        )

        self.assertEqual(wallet.public_key, entropy_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, entropy_constants["secp256k1_classic_address"]
        )

    def test_from_entropy_using_algorithm_ed25519(self):
        wallet = Wallet.from_entropy(
            entropy_constants["entropy"], algorithm=CryptoAlgorithm.ED25519
        )

        self.assertEqual(wallet.public_key, entropy_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, entropy_constants["ed25519_classic_address"]
        )

    def test_from_entropy_using_regular_key_pair_using_default_algorithm(self):
        wallet = Wallet.from_entropy(
            entropy_constants["entropy"],
            master_address=regular_key_pair_constants["master_address"],
        )

        self.assertEqual(wallet.public_key, entropy_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_entropy_using_regular_key_pai_using_algorithm_ed25519(self):
        wallet = Wallet.from_entropy(
            entropy_constants["entropy"],
            master_address=regular_key_pair_constants["master_address"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        self.assertEqual(wallet.public_key, entropy_constants["ed25519_public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["ed25519_private_key"])
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_from_entropy_using_regular_key_pair_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_entropy(
            entropy_constants["entropy"],
            master_address=regular_key_pair_constants["master_address"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        self.assertEqual(wallet.public_key, entropy_constants["secp256k1_public_key"])
        self.assertEqual(wallet.private_key, entropy_constants["secp256k1_private_key"])
        self.assertEqual(
            wallet.classic_address, regular_key_pair_constants["master_address"]
        )

    def test_get_xaddress_when_test_is_true(self):
        self.assertEqual(
            xaddress_wallet.get_xaddress(tag=xaddress_constants["tag"], is_test=True),
            xaddress_constants["testnet_xaddress"],
        )

    def test_get_xaddress_when_test_is_false(self):
        self.assertEqual(
            xaddress_wallet.get_xaddress(tag=xaddress_constants["tag"], is_test=False),
            xaddress_constants["mainnet_xaddress"],
        )

    def test_get_xaddress_when_test_is_not_provided(self):
        self.assertEqual(
            xaddress_wallet.get_xaddress(tag=xaddress_constants["tag"]),
            xaddress_constants["mainnet_xaddress"],
        )

    def test_address_alias(self):
        wallet = Wallet.generate()
        self.assertEqual(wallet.address, wallet.classic_address)

    def test_get_only_address(self):
        wallet = Wallet.generate()

        with self.assertRaises(AttributeError):
            wallet.address = "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc"

        with self.assertRaises(AttributeError):
            wallet.classic_address = "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc"
