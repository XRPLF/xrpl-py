import json
import os
from unittest import TestCase

from xrpl.models.currencies import IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.mptoken_metadata import MPTokenMetadata, MPTokenMetadataUri
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import Payment, PaymentFlag
from xrpl.models.utils import _is_kw_only_attr_defined_in_dataclass
from xrpl.utils.mptoken_metadata import (
    decode_mptoken_metadata,
    encode_mptoken_metadata,
    validate_mptoken_metadata,
)
from xrpl.utils.str_conversions import str_to_hex

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


class TestMPTokenMetadataValidation(TestCase):
    def test_mptoken_metadata_validation_messages(self):
        test_file = os.path.join(
            os.path.dirname(__file__), "mptoken-metadata-validation-fixtures.json"
        )

        with open(test_file, "r", encoding="utf-8") as f:
            test_cases = json.load(f)

        for test_case in test_cases:
            test_name = test_case["testName"]
            mpt_metadata = test_case["mptMetadata"]
            expected_messages = test_case["validationMessages"]

            if isinstance(mpt_metadata, str):
                metadata_str = mpt_metadata
            else:
                metadata_str = json.dumps(mpt_metadata)

            result = validate_mptoken_metadata(str_to_hex(metadata_str))

            with self.subTest(test_name=test_name):
                self.assertEqual(expected_messages, result)


class TestMPTokenMetadataEncodingDecoding(TestCase):
    def test_mptoken_metadata_encoding_decoding(self):
        test_file = os.path.join(
            os.path.dirname(__file__), "mptoken-metadata-encode-decode-fixtures.json"
        )

        with open(test_file, "r", encoding="utf-8") as f:
            test_cases = json.load(f)

        for test_case in test_cases:
            test_name = test_case["testName"]
            mpt_metadata = test_case["mptMetadata"]
            expected_long_form = test_case["expectedLongForm"]
            expected_hex = test_case["hex"]

            encoded_metadata = encode_mptoken_metadata(mpt_metadata)
            decoded_metadata = decode_mptoken_metadata(encoded_metadata)

            with self.subTest(test_name=test_name):
                self.assertEqual(expected_long_form, decoded_metadata)
                self.assertEqual(expected_hex, encoded_metadata)
