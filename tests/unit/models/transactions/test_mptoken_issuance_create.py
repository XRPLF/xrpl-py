from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import MPTokenIssuanceCreate, MPTokenIssuanceCreateFlag
from xrpl.utils import str_to_hex

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestMPTokenIssuanceCreate(TestCase):
    def test_tx_is_valid(self):
        tx = MPTokenIssuanceCreate(
            account=_ACCOUNT,
            maximum_amount="9223372036854775807",  # "7fffffffffffffff"
            asset_scale=2,
            transfer_fee=1,
            flags=2,
            mptoken_metadata=str_to_hex("http://xrpl.org"),
        )
        self.assertTrue(tx.is_valid())

    def test_mptoken_metadata_empty_string(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
                mptoken_metadata="",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'mptoken_metadata': 'Field must not be empty string.'}",
        )

    def test_mptoken_metadata_not_hex(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceCreate(
                account=_ACCOUNT,
                flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK,
                mptoken_metadata="http://xrpl.org",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'mptoken_metadata': 'Field must be in hex format.'}",
        )
