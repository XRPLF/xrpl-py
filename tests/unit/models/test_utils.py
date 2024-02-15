from unittest import TestCase

from xrpl.models.currencies import IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import AccountSet, AccountSetAsfFlag, Payment, PaymentFlag
from xrpl.models.utils import _is_kw_only_attr_defined_in_dataclass

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

currency = "BTC"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"

_DESTINATION = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
_XRP_AMOUNT = "10000"


class TestUtils(TestCase):
    def test_kwargs_req(self):
        if not _is_kw_only_attr_defined_in_dataclass():
            with self.assertRaises(XRPLModelException):
                IssuedCurrency(currency, issuer)
        else:
            with self.assertRaises(TypeError):
                IssuedCurrency(currency, issuer)

    def test_throws_if_positional_args_mixed_with_non_positional_args(self):
        if not _is_kw_only_attr_defined_in_dataclass():
            with self.assertRaises(XRPLModelException):
                Payment(
                    20,
                    True,
                    account=_ACCOUNT,
                    fee=_FEE,
                    sequence=_SEQUENCE,
                    amount=_XRP_AMOUNT,
                    send_max=_XRP_AMOUNT,
                    destination=_DESTINATION,
                    flags=PaymentFlag.TF_PARTIAL_PAYMENT,
                )
        else:
            with self.assertRaises(TypeError):
                Payment(
                    20,
                    True,
                    account=_ACCOUNT,
                    fee=_FEE,
                    sequence=_SEQUENCE,
                    amount=_XRP_AMOUNT,
                    send_max=_XRP_AMOUNT,
                    destination=_DESTINATION,
                    flags=PaymentFlag.TF_PARTIAL_PAYMENT,
                )

    def test_positional_args_in_model_constructor_throws(self):
        if not _is_kw_only_attr_defined_in_dataclass():
            with self.assertRaises(XRPLModelException):
                AccountInfo(
                    "invalidInput",
                    [1, 2, "example invalid positional arg"],
                    account=_ACCOUNT,
                )
        else:
            with self.assertRaises(TypeError):
                AccountInfo(
                    "invalidInput",
                    [1, 2, "example invalid positional arg"],
                    account=_ACCOUNT,
                )
