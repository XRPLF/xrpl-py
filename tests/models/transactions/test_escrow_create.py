from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowCreate


class TestEscrowCreate(TestCase):
    def test_final_after_less_than_cancel_after(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        amount = "amount"
        cancel_after = 1
        finish_after = 2
        destination = "destination"
        fee = "0.00001"
        sequence = 19048

        with self.assertRaises(XRPLModelException):
            EscrowCreate(
                account=account,
                amount=amount,
                cancel_after=cancel_after,
                destination=destination,
                fee=fee,
                finish_after=finish_after,
                sequence=sequence,
            )
