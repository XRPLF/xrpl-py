from unittest import TestCase

from xrpl.models.currencies import IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import Payment, PaymentFlag
from xrpl.models.utils import _is_kw_only_attr_defined_in_dataclass

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048

currency = "BTC"
issuer = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"

_DESTINATION = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
_XRP_AMOUNT = "10000"


class _KW_only_test_context_manager:
    def __init__(self):
        # Newer versions of Python returns a TypeError, unlike the older versions
        self.error_type = (
            TypeError if _is_kw_only_attr_defined_in_dataclass() else XRPLModelException
        )

    # Depending on the version of Python's interpreter, the correct exception type is
    # used for validation
    def __enter__(self):
        return self.error_type

    def __exit__(self, type, value, traceback):
        # upon exit, there is no file or resource to gracefully close
        pass


class TestUtils(TestCase):
    def test_kwargs_req(self):
        with _KW_only_test_context_manager() as exception_type:
            with self.assertRaises(exception_type):
                IssuedCurrency(currency, issuer)

    def test_throws_if_positional_args_mixed_with_non_positional_args(self):
        with _KW_only_test_context_manager() as exception_type:
            with self.assertRaises(exception_type):
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
        with _KW_only_test_context_manager() as exception_type:
            with self.assertRaises(exception_type):
                AccountInfo(
                    "invalidInput",
                    [1, 2, "example invalid positional arg"],
                    account=_ACCOUNT,
                )
