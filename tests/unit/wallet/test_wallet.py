from unittest import TestCase

from xrpl import CryptoAlgorithm
from xrpl.core.addresscodec.exceptions import XRPLAddressCodecException
from xrpl.wallet import Wallet

SEED = "ssQgsaM2ujhyWoDw3Yb1TNjkZTVT2"
SECP_ADDRESS = "r9o97fQwt54s73b1UzgbhvZTPDHYgSqz7G"
ED_ADDRESS = "rnbrEQ9U6TgPkBYuR4RWSWGR1XgaPWuFjh"

SED_SEED = "sEdVRAkrcTVBt4jKfJyKzQzndPFARgs"
SED_ADDRESS = "rLLYAFe2iEGaQrz3rqWfpziGAR4XfQrW3e"


class TestWallet(TestCase):
    def test_create_basic(self):
        wallet = Wallet.create()
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.ED25519)
        self.assertTrue(wallet.seed.startswith("sEd"))

    def test_create_secp(self):
        wallet = Wallet.create(algorithm=CryptoAlgorithm.SECP256K1)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.SECP256K1)
        self.assertFalse(wallet.seed.startswith("sEd"))
        self.assertTrue(wallet.seed.startswith("s"))

    def test_init_auto_with_s_seed(self):
        wallet = Wallet.from_seed(SEED, algorithm=CryptoAlgorithm.SECP256K1)
        self.assertEqual(wallet.seed, SEED)
        self.assertEqual(wallet.classic_address, SECP_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.SECP256K1)

    def test_init_auto_with_sEd_seed(self):
        wallet = Wallet.from_seed(SED_SEED)
        self.assertEqual(wallet.seed, SED_SEED)
        self.assertEqual(wallet.classic_address, SED_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.ED25519)

    def test_init_secp256k1_with_s_seed(self):
        wallet = Wallet.from_seed(SEED, algorithm=CryptoAlgorithm.SECP256K1)
        self.assertEqual(wallet.seed, SEED)
        self.assertEqual(wallet.classic_address, SECP_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.SECP256K1)

    def test_init_ed25519_with_s_seed(self):
        wallet = Wallet.from_seed(SEED, algorithm=CryptoAlgorithm.ED25519)
        self.assertEqual(wallet.seed, SEED)
        self.assertEqual(wallet.address, ED_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.ED25519)

    def test_init_secp256k1_with_sEd_seed_fail(self):
        with self.assertRaises(XRPLAddressCodecException):
            Wallet.from_seed(SED_SEED, algorithm=CryptoAlgorithm.SECP256K1)
