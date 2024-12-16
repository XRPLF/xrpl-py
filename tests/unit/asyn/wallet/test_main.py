from unittest import TestCase

from xrpl.constants import CryptoAlgorithm, XRPLException
from xrpl.core.addresscodec.exceptions import XRPLAddressCodecException
from xrpl.wallet.main import Wallet

constants = {
    "regular_key_pair": {
        "master_address": "rUAi7pipxGpYfPNg3LtPcf2ApiS8aw9A93",
        "seed": "sh8i92YRnEjJy3fpFkL8txQSCVo79",
        "ed25519": {
            "public_key": "ED848AB5972C2D7885DBF188EAF1DC24C3EE8064E41C13AAFF3B731494B9C81990",  # noqa:E501
            "private_key": "ED14CAA44B431CEE77F13139BFDE59F63CBEBCFF37C6F0F4AC6F05620A5EDBE33C",  # noqa:E501
        },
        "secp256k1": {
            "public_key": "03AEEFE1E8ED4BBC009DE996AC03A8C6B5713B1554794056C66E5B8D1753C7DD0E",  # noqa:E501
            "private_key": "004265A28F3E18340A490421D47B2EB8DBC2C0BF2C24CEFEA971B61CED2CABD233",  # noqa:E501
        },
    },
    "seed": {
        "seed": "ssL9dv2W5RK8L3tuzQxYY6EaZhSxW",
        "ed25519": {
            "public_key": "ED16FD02F7A7E52B6ACB35F8A4D7013DC94755951629DB6611483590AC0E9FC6D5",  # noqa:E501
            "private_key": "ED713A8C3171A3D8F69FE9526D9243834B3A30BF893B1EBC1824B1D96F18B44DCF",  # noqa:E501
            "address": "rPxLJ2GumwfLk3z9njmmpo8nAX7sfZYptV",
        },
        "secp256k1": {
            "public_key": "030E58CDD076E798C84755590AAF6237CA8FAE821070A59F648B517A30DC6F589D",  # noqa:E501
            "private_key": "00141BA006D3363D2FB2785E8DF4E44D3A49908780CB4FB51F6D217C08C021429F",  # noqa:E501
            "address": "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc",
        },
    },
    "entropy": {
        "entropy": "00000000000000000000000000000000",
        "ed25519": {
            "seed": "sEdSJHS4oiAdz7w2X2ni1gFiqtbJHqE",
            "public_key": "ED1A7C082846CFF58FF9A892BA4BA2593151CCF1DBA59F37714CC9ED39824AF85F",  # noqa:E501
            "private_key": "ED0B6CBAC838DFE7F47EA1BD0DF00EC282FDF45510C92161072CCFB84035390C4D",  # noqa:E501
            "address": "r9zRhGr7b6xPekLvT6wP4qNdWMryaumZS7",
        },
        "secp256k1": {
            "seed": "sp6JS7f14BuwFY8Mw6bTtLKWauoUs",
            "public_key": "0390A196799EE412284A5D80BF78C3E84CBB80E1437A0AECD9ADF94D7FEAAFA284",  # noqa:E501
            "private_key": "002512BBDFDBB77510883B7DCCBEF270B86DEAC8B64AC762873D75A1BEE6298665",  # noqa:E501
            "address": "rGCkuB7PBr5tNy68tPEABEtcdno4hE6Y7f",
        },
    },
    "secret_numbers": {
        "string": "399150 474506 009147 088773 432160 282843 253738 605430",
        "array": [
            "399150",
            "474506",
            "009147",
            "088773",
            "432160",
            "282843",
            "253738",
            "605430",
        ],
        "ed25519": {
            "seed": "sEd77GiNwRkBYwqzZiTrmh21oovzSAC",
            "public_key": "ED8079E575450E256C496578480020A33E19B579D58A2DB8FF13FC6B05B9229DE3",  # noqa:E501
            "private_key": "EDD2AF6288A903DED9860FC62E778600A985BDF804E40BD8266505553E3222C3DA",  # noqa:E501
            "address": "rHnnXF4oYodLonx7P7MV4WaqPUvBWzskEw",
        },
        "secp256k1": {
            "seed": "sh1HiK7SwjS1VxFdXi7qeMHRedrYX",
            "public_key": "03BFC2F7AE242C3493187FA0B72BE97B2DF71194FB772E507FF9DEA0AD13CA1625",  # noqa:E501
            "private_key": "00B6FE8507D977E46E988A8A94DB3B8B35E404B60F8B11AC5213FA8B5ABC8A8D19",  # noqa:E501
            "address": "rQKQsPeE3iTRyfUypLhuq74gZdcRdwWqDp",
        },
    },
    "prefix": {
        "address": "r",
        "ed25519_key": "ED",
        "secp256k1_private_key": "00",
    },
    "xaddress": {
        "tag": 1337,
        "mainnet_xaddress": "X7gJ5YK8abHf2eTPWPFHAAot8Knck11QGqmQ7a6a3Z8PJvk",
        "testnet_xaddress": "T7bq3e7kxYq9pwDz8UZhqAZoEkcRGTXSNr5immvcj3DYRaV",
        "wallet": Wallet(
            "030E58CDD076E798C84755590AAF6237CA8FAE821070A59F648B517A30DC6F589D",
            "00141BA006D3363D2FB2785E8DF4E44D3A49908780CB4FB51F6D217C08C021429F",
        ),
    },
}


def _test_wallet_values(
    self, wallet, method, algorithm, *, is_entropy_with_regular_key_pair=False
):
    method_constants = constants[method]
    algorithm_constants = method_constants[algorithm]

    self.assertEqual(wallet.public_key, algorithm_constants["public_key"])
    self.assertEqual(wallet.private_key, algorithm_constants["private_key"])

    if method == "entropy" or method == "secret_numbers":
        self.assertEqual(wallet.seed, algorithm_constants["seed"])
    else:
        self.assertEqual(wallet.seed, method_constants["seed"])

    if method == "regular_key_pair" or is_entropy_with_regular_key_pair:
        self.assertEqual(
            wallet.address, constants["regular_key_pair"]["master_address"]
        )
    else:
        self.assertEqual(wallet.address, algorithm_constants["address"])


def _test_wallet_types(self, wallet, algorithm):
    self.assertIsInstance(wallet.public_key, str)
    self.assertIsInstance(wallet.private_key, str)
    self.assertIsInstance(wallet.address, str)
    self.assertIsInstance(wallet.address, str)
    self.assertIsInstance(wallet.seed, str)
    self.assertTrue(wallet.address.startswith(constants["prefix"]["address"]))

    if algorithm == "ed25519":
        self.assertTrue(
            wallet.public_key.startswith(constants["prefix"]["ed25519_key"])
        )
        self.assertTrue(
            wallet.private_key.startswith(constants["prefix"]["ed25519_key"])
        )
    else:
        self.assertTrue(
            wallet.private_key.startswith(constants["prefix"]["secp256k1_private_key"])
        )


class TestWalletMain(TestCase):
    def test_constructor(self):
        wallet = Wallet(
            constants["seed"]["secp256k1"]["public_key"],
            constants["seed"]["secp256k1"]["private_key"],
            seed=constants["seed"]["seed"],
        )

        _test_wallet_values(self, wallet, "seed", "secp256k1")

    def test_wallet_contructor_throws_with_invalid_seed(self):
        with self.assertRaises(XRPLAddressCodecException):
            Wallet(
                constants["regular_key_pair"]["secp256k1"]["public_key"],
                constants["regular_key_pair"]["secp256k1"]["private_key"],
                seed="abc",
            )

    def test_constructor_using_regular_key_pair(self):
        wallet = Wallet(
            constants["regular_key_pair"]["secp256k1"]["public_key"],
            constants["regular_key_pair"]["secp256k1"]["private_key"],
            master_address=constants["regular_key_pair"]["master_address"],
            seed=constants["regular_key_pair"]["seed"],
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "secp256k1")

    def test_create_using_default_algorithm(self):
        wallet = Wallet.create()

        _test_wallet_types(self, wallet, "ed25519")

    def test_create_using_algorithm_ed25519(self):
        wallet = Wallet.create(CryptoAlgorithm.ED25519)

        _test_wallet_types(self, wallet, "ed25519")

    def test_create_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.create(CryptoAlgorithm.SECP256K1)

        _test_wallet_types(self, wallet, "secp256k1")

    def test_from_seed_using_default_algorithm(self):
        wallet = Wallet.from_seed(constants["seed"]["seed"])

        _test_wallet_values(self, wallet, "seed", "ed25519")

    def test_from_seed_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_seed(
            constants["seed"]["seed"], algorithm=CryptoAlgorithm.SECP256K1
        )

        _test_wallet_values(self, wallet, "seed", "secp256k1")

    def test_from_seed_using_algorithm_ed25519(self):
        wallet = Wallet.from_seed(
            constants["seed"]["seed"], algorithm=CryptoAlgorithm.ED25519
        )

        _test_wallet_values(self, wallet, "seed", "ed25519")

    def test_from_seed_using_regular_key_pair_using_default_algorithm(self):
        wallet = Wallet.from_seed(
            constants["regular_key_pair"]["seed"],
            master_address=constants["regular_key_pair"]["master_address"],
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "ed25519")

    def test_from_seed_using_regular_key_pair_using_algorithm_ed25519(self):
        wallet = Wallet.from_seed(
            constants["regular_key_pair"]["seed"],
            master_address=constants["regular_key_pair"]["master_address"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "ed25519")

    def test_from_seed_using_regular_key_pair_using_algorithm_edcsa_secp256k1(self):
        wallet = Wallet.from_seed(
            constants["regular_key_pair"]["seed"],
            master_address=constants["regular_key_pair"]["master_address"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "secp256k1")

    def test_from_secret_using_default_algorithm(self):
        wallet = Wallet.from_secret(constants["seed"]["seed"])

        _test_wallet_values(self, wallet, "seed", "ed25519")

    def test_from_secret_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_secret(
            constants["seed"]["seed"], algorithm=CryptoAlgorithm.SECP256K1
        )

        _test_wallet_values(self, wallet, "seed", "secp256k1")

    def test_from_secret_using_algorithm_ed25519(self):
        wallet = Wallet.from_secret(
            constants["seed"]["seed"], algorithm=CryptoAlgorithm.ED25519
        )

        _test_wallet_values(self, wallet, "seed", "ed25519")

    def test_from_secret_using_regular_key_pair_using_default_algorithm(self):
        wallet = Wallet.from_secret(
            constants["regular_key_pair"]["seed"],
            master_address=constants["regular_key_pair"]["master_address"],
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "ed25519")

    def test_from_secret_using_regular_key_pair_using_algorithm_ed25519(self):
        wallet = Wallet.from_secret(
            constants["regular_key_pair"]["seed"],
            master_address=constants["regular_key_pair"]["master_address"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "ed25519")

    def test_from_secret_using_regular_key_pair_using_algorithm_edcsa_secp256k1(self):
        wallet = Wallet.from_secret(
            constants["regular_key_pair"]["seed"],
            master_address=constants["regular_key_pair"]["master_address"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        _test_wallet_values(self, wallet, "regular_key_pair", "secp256k1")

    def test_from_entropy_using_default_algorithm(self):
        wallet = Wallet.from_entropy(constants["entropy"]["entropy"])

        _test_wallet_values(self, wallet, "entropy", "ed25519")

    def test_from_entropy_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_entropy(
            constants["entropy"]["entropy"], algorithm=CryptoAlgorithm.SECP256K1
        )

        _test_wallet_values(self, wallet, "entropy", "secp256k1")

    def test_from_entropy_using_algorithm_ed25519(self):
        wallet = Wallet.from_entropy(
            constants["entropy"]["entropy"], algorithm=CryptoAlgorithm.ED25519
        )

        _test_wallet_values(self, wallet, "entropy", "ed25519")

    def test_from_entropy_using_regular_key_pair_using_default_algorithm(self):
        wallet = Wallet.from_entropy(
            constants["entropy"]["entropy"],
            master_address=constants["regular_key_pair"]["master_address"],
        )

        _test_wallet_values(
            self, wallet, "entropy", "ed25519", is_entropy_with_regular_key_pair=True
        )

    def test_from_entropy_using_regular_key_pair_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_entropy(
            constants["entropy"]["entropy"],
            master_address=constants["regular_key_pair"]["master_address"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        _test_wallet_values(
            self, wallet, "entropy", "secp256k1", is_entropy_with_regular_key_pair=True
        )

    def test_from_entropy_using_regular_key_pair_using_algorithm_ed25519(self):
        wallet = Wallet.from_entropy(
            constants["entropy"]["entropy"],
            master_address=constants["regular_key_pair"]["master_address"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        _test_wallet_values(
            self, wallet, "entropy", "ed25519", is_entropy_with_regular_key_pair=True
        )

    def test_from_secret_numbers_string_using_default_algorithm(self):
        wallet = Wallet.from_secret_numbers(constants["secret_numbers"]["string"])

        _test_wallet_values(self, wallet, "secret_numbers", "ed25519")

    def test_from_secret_numbers_array_using_default_algorithm(self):
        wallet = Wallet.from_secret_numbers(constants["secret_numbers"]["array"])

        _test_wallet_values(self, wallet, "secret_numbers", "ed25519")

    def test_from_secret_numbers_string_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_secret_numbers(
            constants["secret_numbers"]["string"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        _test_wallet_values(self, wallet, "secret_numbers", "secp256k1")

    def test_from_secret_numbers_array_using_algorithm_ecdsa_secp256k1(self):
        wallet = Wallet.from_secret_numbers(
            constants["secret_numbers"]["array"],
            algorithm=CryptoAlgorithm.SECP256K1,
        )

        _test_wallet_values(self, wallet, "secret_numbers", "secp256k1")

    def test_from_secret_numbers_string_using_algorithm_ed25519(self):
        wallet = Wallet.from_secret_numbers(
            constants["secret_numbers"]["string"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        _test_wallet_values(self, wallet, "secret_numbers", "ed25519")

    def test_from_secret_numbers_array_using_algorithm_ed25519(self):
        wallet = Wallet.from_secret_numbers(
            constants["secret_numbers"]["array"],
            algorithm=CryptoAlgorithm.ED25519,
        )

        _test_wallet_values(self, wallet, "secret_numbers", "ed25519")

    def test_from_secret_numbers_failure_nine_numbers(self):
        invalid_array = constants["secret_numbers"]["array"].copy()
        invalid_array.append("605430")

        with self.assertRaises(XRPLException):
            Wallet.from_secret_numbers(
                invalid_array,
                algorithm=CryptoAlgorithm.ED25519,
            )

    def test_from_secret_numbers_failure_seven_digit_number(self):
        invalid_array = constants["secret_numbers"]["array"].copy()
        invalid_array[0] += "1"

        with self.assertRaises(XRPLException):
            Wallet.from_secret_numbers(
                invalid_array,
                algorithm=CryptoAlgorithm.ED25519,
            )

    def test_get_xaddress_when_test_is_true(self):
        self.assertEqual(
            constants["xaddress"]["wallet"].get_xaddress(
                tag=constants["xaddress"]["tag"], is_test=True
            ),
            constants["xaddress"]["testnet_xaddress"],
        )

    def test_get_xaddress_when_test_is_false(self):
        self.assertEqual(
            constants["xaddress"]["wallet"].get_xaddress(
                tag=constants["xaddress"]["tag"], is_test=False
            ),
            constants["xaddress"]["mainnet_xaddress"],
        )

    def test_get_xaddress_when_test_is_not_provided(self):
        self.assertEqual(
            constants["xaddress"]["wallet"].get_xaddress(
                tag=constants["xaddress"]["tag"]
            ),
            constants["xaddress"]["mainnet_xaddress"],
        )

    def test_address_alias(self):
        wallet = Wallet.create()
        self.assertEqual(wallet.address, wallet.address)

    def test_get_only_address(self):
        wallet = Wallet.create()

        with self.assertRaises(AttributeError):
            wallet.address = "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc"

        with self.assertRaises(AttributeError):
            wallet.address = "rhvh5SrgBL5V8oeV9EpDuVszeJSSCEkbPc"
