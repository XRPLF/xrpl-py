from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowCreate

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rJXXwHs6YYZmomBnJoYQdxwXSwJq56tJBn"


class TestEscrowCreate(TestCase):
    def test_final_after_less_than_cancel_after(self):
        account = _SOURCE
        amount = "10.890"
        cancel_after = 1
        finish_after = 2
        destination = _DESTINATION
        fee = "0.00001"
        sequence = 19048

        with self.assertRaises(XRPLModelException) as error:
            EscrowCreate(
                account=account,
                amount=amount,
                cancel_after=cancel_after,
                destination=destination,
                fee=fee,
                finish_after=finish_after,
                sequence=sequence,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'EscrowCreate': "
            "'The finish_after time must be before the cancel_after time.'}",
        )

    def test_amount_not_postive(self):
        with self.assertRaises(XRPLModelException) as error:
            EscrowCreate(
                account=_SOURCE,
                destination=_DESTINATION,
                amount=IssuedCurrencyAmount(
                    issuer="rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy",
                    currency="USD",
                    value="0.00",
                ),
                cancel_after=10,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'amount': 'amount must be positive.'}",
        )

    def test_cancel_after_missing_on_mpt(self):
        with self.assertRaises(XRPLModelException) as error:
            EscrowCreate(
                account=_SOURCE,
                destination=_DESTINATION,
                amount=MPTAmount(
                    mpt_issuance_id="rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy",
                    value="10.20",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'cancel_after': "
            "'cancel_after is required when creating an Escrow with IOU or MPT.'}",
        )

    def test_valid_escrow_create(self):
        tx = EscrowCreate(
            account=_SOURCE,
            destination=_DESTINATION,
            amount=MPTAmount(
                mpt_issuance_id="rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy",
                value="10.20",
            ),
            cancel_after=10,
        )
        self.assertTrue(tx.is_valid())
