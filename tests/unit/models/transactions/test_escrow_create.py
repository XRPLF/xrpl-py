from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import EscrowCreate

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rJXXwHs6YYZmomBnJoYQdxwXSwJq56tJBn"


class TestEscrowCreate(TestCase):
    def test_all_fields_valid(self):
        account = _SOURCE
        amount = "1000"
        cancel_after = 3
        destination = _DESTINATION
        destination_tag = 1
        finish_after = 2
        finish_function = "abcdef"
        condition = "abcdef"

        escrow_create = EscrowCreate(
            account=account,
            amount=amount,
            destination=destination,
            destination_tag=destination_tag,
            cancel_after=cancel_after,
            finish_after=finish_after,
            finish_function=finish_function,
            condition=condition,
        )
        self.assertTrue(escrow_create.is_valid())

    def test_final_after_less_than_cancel_after(self):
        account = _SOURCE
        amount = "10.890"
        cancel_after = 1
        finish_after = 2
        destination = _DESTINATION

        with self.assertRaises(XRPLModelException) as error:
            EscrowCreate(
                account=account,
                amount=amount,
                cancel_after=cancel_after,
                destination=destination,
                finish_after=finish_after,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'EscrowCreate': "
            "'The finish_after time must be before the cancel_after time.'}",
        )

    def test_no_finish(self):
        account = _SOURCE
        amount = "1000"
        cancel_after = 1
        destination = _DESTINATION
        destination_tag = 1

        with self.assertRaises(XRPLModelException) as error:
            EscrowCreate(
                account=account,
                amount=amount,
                destination=destination,
                destination_tag=destination_tag,
                cancel_after=cancel_after,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'EscrowCreate': "
            "'At least one of finish_after, condition, or finish_function must be set.'"
            "}",
        )

    def test_amount_not_positive(self):
        with self.assertRaises(XRPLModelException) as error:
            EscrowCreate(
                account=_SOURCE,
                destination=_DESTINATION,
                amount=IssuedCurrencyAmount(
                    issuer="rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy",
                    currency="USD",
                    value="0.00",
                ),
                finish_after=10,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'amount': 'amount must be positive.'}",
        )

    def test_valid_escrow_create(self):
        tx = EscrowCreate(
            account=_SOURCE,
            destination=_DESTINATION,
            amount=MPTAmount(
                mpt_issuance_id="rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy",
                value="10.20",
            ),
            finish_after=10,
        )
        self.assertTrue(tx.is_valid())
