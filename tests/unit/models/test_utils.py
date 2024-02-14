from unittest import TestCase

from xrpl.constants import CryptoAlgorithm
from xrpl.models.currencies import IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import ChannelAuthorize, Sign
from xrpl.models.transactions import AccountSet, AccountSetAsfFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_DOMAIN = "asjcsodafsaid0f9asdfasdf"
_TRANSACTION = AccountSet(
    account=_ACCOUNT,
    fee=_FEE,
    set_flag=AccountSetAsfFlag.ASF_DISALLOW_XRP,
    domain=_DOMAIN,
    sequence=_SEQUENCE,
)

_SEED = "randomsecretseedforakey"

_CHANNEL_ID = "5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5BDB3"
_AMOUNT = "10000"
_DUMMY_STRING = "loremipsem"

currency = "BTC"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestUtils(TestCase):
    def test_kwargs_req(self):
        with self.assertRaises(XRPLModelException):
            IssuedCurrency(currency, issuer)

    def test_throws_if_positional_args_mixed_with_non_positional_args(self):
        with self.assertRaises(XRPLModelException):
            ChannelAuthorize(
                20,
                True,
                channel_id=_CHANNEL_ID,
                amount=_AMOUNT,
                passphrase=_DUMMY_STRING,
                seed_hex=_DUMMY_STRING,
            )

    def test_positional_args_in_ledger_objects_constructor_throws(self):
        with self.assertRaises(XRPLModelException):
            Sign(
                "invalidInput",
                [1, 2, "example invalid positional arg"],
                transaction=_TRANSACTION,
                seed=_SEED,
                key_type=CryptoAlgorithm.SECP256K1,
            )
