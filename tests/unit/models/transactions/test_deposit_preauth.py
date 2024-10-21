from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import DepositPreauth
from xrpl.models.transactions.deposit_preauth import Credential

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestDepositPreauth(TestCase):
    def test_all_input_combinations(self):
        # this value is used for authorized_credentials or unauthorized_credentials
        # fields
        sample_credentials = [
            Credential(issuer="SampleIssuer", credential_type="SampleCredType")
        ]
        for val in range(0, 16):
            # bitmap
            # 0'th bit represents authorize field
            # 1'th bit represents unauthorize field
            # 2'nd bit represents authorized_credentials field
            # 3'rd bit represents unauthorized_credentials field

            if val in [1, 2, 4, 8]:  # all the valid input cases
                tx = DepositPreauth(
                    account=_ACCOUNT,
                    fee=_FEE,
                    sequence=_SEQUENCE,
                    authorize="authorize" if (val & 1) != 0 else None,
                    unauthorize="unauthorize" if (val & 2) != 0 else None,
                    authorize_credentials=(
                        sample_credentials if (val & 4) != 0 else None
                    ),
                    unauthorize_credentials=(
                        sample_credentials if (val & 8) != 0 else None
                    ),
                )
                self.assertTrue(tx.is_valid())
            else:
                with self.assertRaises(XRPLModelException) as error:
                    DepositPreauth(
                        account=_ACCOUNT,
                        fee=_FEE,
                        sequence=_SEQUENCE,
                        authorize="authorize" if (val & 1) != 0 else None,
                        unauthorize="unauthorize" if (val & 2) != 0 else None,
                        authorize_credentials=(
                            sample_credentials if (val & 4) != 0 else None
                        ),
                        unauthorize_credentials=(
                            sample_credentials if (val & 8) != 0 else None
                        ),
                    )

                # capture the case where no field was specified as input
                if val == 0:
                    self.assertEqual(
                        error.exception.args[0],
                        "{'DepositPreauth': '"
                        + "Exactly one input parameter amongst authorize, unauthorize, "
                        + "authorize_credentials or unauthorize_credentials must be set"
                        + "."
                        + " It is "
                        + "invalid if none of the params are specified."
                        + "'}",
                    )
                # capture the case where a plurality of inputs are specified
                else:
                    self.assertEqual(
                        error.exception.args[0],
                        "{'DepositPreauth': '"
                        + "More than one input param cannot be specified for "
                        + "DepositPreauth "
                        + "transaction. Please specify exactly one input parameter. "
                        + "'}",
                    )

    # Unit tests validating the length of array inputs
    def test_authcreds_array_input_exceed_length_check(self):
        # Note: If credentials de-duplication is implemented in the client library,
        # additional tests need to be written
        sample_credentials = [
            Credential(
                issuer="SampleIssuer_" + str(i), credential_type="SampleCredType"
            )
            for i in range(9)
        ]

        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize_credentials=sample_credentials,
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth_authorize_credentials': '"
            + "AuthorizeCredentials list cannot have more than 8 elements. "
            + "'}",
        )

    def test_authcreds_empty_array_inputs(self):
        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                authorize_credentials=[],
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth_authorize_credentials': '"
            + "AuthorizeCredentials list cannot be empty. "
            + "'}",
        )

    def test_unauthcreds_array_input_exceed_length_check(self):
        # Note: If credentials de-duplication is implemented in the client library,
        # additional tests need to be written
        sample_credentials = [
            Credential(
                issuer="SampleIssuer_" + str(i), credential_type="SampleCredType"
            )
        ]*9

        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                unauthorize_credentials=sample_credentials,
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth_unauthorize_credentials': '"
            + "UnauthorizeCredentials list cannot have more than 8 elements. "
            + "'}",
        )

    def test_unauthcreds_empty_array_inputs(self):
        with self.assertRaises(XRPLModelException) as error:
            DepositPreauth(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                unauthorize_credentials=[],
            )

        self.assertEqual(
            error.exception.args[0],
            "{'DepositPreauth_unauthorize_credentials': '"
            + "UnauthorizeCredentials list cannot be empty. "
            + "'}",
        )
