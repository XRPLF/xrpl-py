from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import NFTokenCancelOffer

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_TOKEN_ID = "00090032B5F762798A53D543A014CAF8B297CFF8F2F937E844B17C9E00000003"


class TestNFTokenCancelOffer(TestCase):
    def test_empty_token_ids(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCancelOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                token_ids=[],
            )

    def test_present_token_ids(self):
        tx = NFTokenCancelOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            token_ids=[_TOKEN_ID],
        )
        self.assertTrue(tx.is_valid())
