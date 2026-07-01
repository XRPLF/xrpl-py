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

    def test_init_auto_with_default_algorithm(self):
        wallet = Wallet.from_seed(SED_SEED)
        self.assertEqual(wallet.seed, SED_SEED)
        self.assertEqual(wallet.address, SED_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.ED25519)

    def test_init_auto_with_sEd_seed(self):
        wallet = Wallet.from_seed(SED_SEED)
        self.assertEqual(wallet.seed, SED_SEED)
        self.assertEqual(wallet.address, SED_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.ED25519)

    def test_init_secp256k1_with_s_seed(self):
        wallet = Wallet.from_seed(SEED, algorithm=CryptoAlgorithm.SECP256K1)
        self.assertEqual(wallet.seed, SEED)
        self.assertEqual(wallet.address, SECP_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.SECP256K1)

    def test_init_ed25519_with_s_seed(self):
        wallet = Wallet.from_seed(SEED, algorithm=CryptoAlgorithm.ED25519)
        self.assertEqual(wallet.seed, SEED)
        self.assertEqual(wallet.address, ED_ADDRESS)
        self.assertEqual(wallet.algorithm, CryptoAlgorithm.ED25519)

    def test_init_secp256k1_with_sEd_seed_fail(self):
        with self.assertRaises(XRPLAddressCodecException):
            Wallet.from_seed(SED_SEED, algorithm=CryptoAlgorithm.SECP256K1)

    def test_invalid_seed_not_leaked_in_exception(self):
        """Regression test for issue #987: exception messages for invalid
        seeds must not include the raw seed, since they often get logged or
        captured by error-tracking systems."""
        secret_seed = "sInvalidSeedXXXXXXXXXXXXXX"
        with self.assertRaises(XRPLAddressCodecException) as ctx:
            Wallet(public_key="abc", private_key="def", seed=secret_seed)
        self.assertNotIn(secret_seed, str(ctx.exception))

    def test_invalid_seed_chars_not_leaked_via_base58_value_error(self):
        """The XRPL base58 alphabet excludes '0', 'O', 'I', and 'l'. When a
        seed contains any of these, ``base58.b58decode`` raises
        ``ValueError("Invalid character '0' ...")`` with the offending byte
        embedded in the message. ``Wallet.__init__`` must neither concatenate
        ``str(e)`` into its own message nor leave the original exception
        attached as ``__cause__`` / ``__context__``, since either path leaks
        a character of the seed into logs and tracebacks.
        """
        # Every character below is in the base58 alphabet *except* '0', so
        # any '0' in the message or chained cause could only have come from
        # the seed.
        seed = "sZZZZZZZZZZZZZZZZZZZZZZZZ0"
        with self.assertRaises(XRPLAddressCodecException) as ctx:
            Wallet(public_key="abc", private_key="def", seed=seed)

        exc = ctx.exception
        self.assertNotIn(seed, str(exc))
        self.assertNotIn("0", str(exc))
        # ``raise ... from None`` must suppress the chained cause so that
        # the original ``ValueError("Invalid character '0'")`` can't reach
        # full-traceback log sinks.
        self.assertIsNone(exc.__cause__)
        self.assertTrue(exc.__suppress_context__)
