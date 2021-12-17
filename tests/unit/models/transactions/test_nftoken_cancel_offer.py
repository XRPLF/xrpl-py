from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import NFTokenCancelOffer

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_TOKEN_OFFER = "3A35B2A4EDF2F3BEF5323C895259957405F0B8F8F6D6E97E46BFDB2484261AF7"


class TestNFTokenCancelOffer(TestCase):
    def test_empty_token_offers(self):
        with self.assertRaises(XRPLModelException):
            NFTokenCancelOffer(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                token_offers=[],
            )

    def test_present_token_offers(self):
        tx = NFTokenCancelOffer(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            token_offers=[_TOKEN_OFFER],
        )
        self.assertTrue(tx.is_valid())
