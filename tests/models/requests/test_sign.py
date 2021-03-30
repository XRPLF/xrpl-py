from unittest import TestCase

from xrpl.constants import CryptoAlgorithm
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import Sign
from xrpl.models.transactions import AccountSet

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_DOMAIN = "asjcsodafsaid0f9asdfasdf"
_TRANSACTION = AccountSet(
    account=_ACCOUNT,
    fee=_FEE,
    set_flag=3,
    domain=_DOMAIN,
    sequence=_SEQUENCE,
)

_SECRET = "randomsecretkey"
_SEED = "randomsecretseedforakey"
_SEED_HEX = "EACEB081770D8ADE216C85445DD6FB002C6B5A2930F2DECE006DA18150CB18F6"
_PASSPHRASE = "mytopsecretpassphrasethatwillneverbehacked"


class TestSign(TestCase):
    def test_invalid_secret_and_seed(self):
        with self.assertRaises(XRPLModelException):
            Sign(transaction=_TRANSACTION, secret=_SECRET, seed=_SEED)

    def test_invalid_seed_and_seed_hex(self):
        with self.assertRaises(XRPLModelException):
            Sign(
                transaction=_TRANSACTION,
                seed=_SEED,
                seed_hex=_SEED_HEX,
            )

    def test_invalid_seed_hex_and_passphrase(self):
        with self.assertRaises(XRPLModelException):
            Sign(
                transaction=_TRANSACTION,
                seed_hex=_SEED_HEX,
                passphrase=_PASSPHRASE,
            )

    def test_invalid_secret_and_passphrase(self):
        with self.assertRaises(XRPLModelException):
            Sign(
                transaction=_TRANSACTION,
                secret=_SECRET,
                passphrase=_PASSPHRASE,
            )

    def test_invalid_secret_and_key_type(self):
        with self.assertRaises(XRPLModelException):
            Sign(
                transaction=_TRANSACTION,
                secret=_SECRET,
                key_type="secp256k1",
            )

    def test_valid_secret(self):
        request = Sign(
            transaction=_TRANSACTION,
            secret=_SECRET,
        )
        self.assertTrue(request.is_valid())

    def test_valid_seed(self):
        request = Sign(
            transaction=_TRANSACTION, seed=_SEED, key_type=CryptoAlgorithm.SECP256K1
        )
        self.assertTrue(request.is_valid())
