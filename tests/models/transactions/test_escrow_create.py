from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions import EscrowCreate


class TestEscrowCreate(TestCase):
    def test_final_after_less_than_cancel_after(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 19048
        amount = "amount"
        destination = "destination"
        cancel_after = 2
        finish_after = 1

        with self.assertRaises(XRPLModelValidationException):
            EscrowCreate(
                account=account,
                fee=fee,
                sequence=sequence,
                amount=amount,
                destination=destination,
                cancel_after=cancel_after,
                finish_after=finish_after,
            )
