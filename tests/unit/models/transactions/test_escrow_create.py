from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowCreate


class TestEscrowCreate(TestCase):
    def test_all_fields_valid(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        amount = "amount"
        cancel_after = 3
        destination = "destination"
        destination_tag = 1
        fee = "0.00001"
        finish_after = 2
        finish_function = "abcdef"
        condition = "abcdef"

        escrow_create = EscrowCreate(
            account=account,
            amount=amount,
            destination=destination,
            destination_tag=destination_tag,
            fee=fee,
            cancel_after=cancel_after,
            finish_after=finish_after,
            finish_function=finish_function,
            condition=condition,
        )
        self.assertTrue(escrow_create.is_valid())

    def test_final_after_less_than_cancel_after(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        amount = "amount"
        cancel_after = 1
        finish_after = 2
        destination = "destination"
        fee = "0.00001"

        with self.assertRaises(XRPLModelException):
            EscrowCreate(
                account=account,
                amount=amount,
                cancel_after=cancel_after,
                destination=destination,
                fee=fee,
                finish_after=finish_after,
            )

    def test_no_finish(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        amount = "amount"
        cancel_after = 1
        destination = "destination"
        destination_tag = 1
        fee = "0.00001"
        sequence = 19048

        with self.assertRaises(XRPLModelException):
            EscrowCreate(
                account=account,
                amount=amount,
                destination=destination,
                destination_tag=destination_tag,
                fee=fee,
                cancel_after=cancel_after,
                sequence=sequence,
            )
