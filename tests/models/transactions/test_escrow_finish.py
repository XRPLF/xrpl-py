from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowFinish

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_OFFER_SEQUENCE = 1
_OWNER = "rJZdUusLDtY9NEsGea7ijqhVrXv98rYBYN"
_SEQUENCE = 19048


class TestEscrowFinish(TestCase):
    def test_fulfillment_set_condition_unset(self):
        fulfillment = "fulfillment"

        with self.assertRaises(XRPLModelException):
            EscrowFinish(
                account=_ACCOUNT,
                fee=_FEE,
                fulfillment=fulfillment,
                offer_sequence=_OFFER_SEQUENCE,
                owner=_OWNER,
                sequence=_SEQUENCE,
            )

    def test_condition_set_fulfillment_unset(self):
        condition = "condition"

        with self.assertRaises(XRPLModelException):
            EscrowFinish(
                account=_ACCOUNT,
                condition=condition,
                fee=_FEE,
                offer_sequence=_OFFER_SEQUENCE,
                owner=_OWNER,
                sequence=_SEQUENCE,
            )
