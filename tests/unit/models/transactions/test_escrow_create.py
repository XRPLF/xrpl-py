from os import urandom
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.models.transactions.escrow_create import generate_escrow_cryptoconditions

_OFFER_SEQUENCE = 1
_OWNER = "rJZdUusLDtY9NEsGea7ijqhVrXv98rYBYN"


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

    def test_escrow_condition_and_fulfillment(self):
        account = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        amount = "100"
        destination = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
        fee = "0.00001"
        sequence = 19048

        # use os.urandom as the source of cryptographic randomness
        condition, fulfillment = generate_escrow_cryptoconditions(urandom(32))

        EscrowCreate(
            account=account,
            amount=amount,
            destination=destination,
            fee=fee,
            sequence=sequence,
            condition=condition,
        )

        # EscrowFinish without the fullfillment must throw an error
        with self.assertRaises(XRPLModelException):
            EscrowFinish(
                account=account,
                condition=condition,
                fee=fee,
                sequence=sequence,
                offer_sequence=_OFFER_SEQUENCE,
                owner=_OWNER,
            )

        # execute Escrow finish with the fulfillment
        EscrowFinish(
            account=account,
            condition=condition,
            fee=fee,
            sequence=sequence,
            fulfillment=fulfillment,
            offer_sequence=_OFFER_SEQUENCE,
            owner=_OWNER,
        )
