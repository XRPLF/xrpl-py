from unittest import TestCase

from xrpl.models import Batch, BatchFlag, Payment, TransactionFlag
from xrpl.models.exceptions import XRPLModelException

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg"


class TestBatch(TestCase):
    def test_basic(self):
        payment = Payment(
            account=_ACCOUNT,
            amount="1",
            destination=_DESTINATION,
        )
        batch = Batch(
            account=_ACCOUNT,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment],
        )
        self.assertTrue(batch.is_valid())
        self.assertTrue(
            batch.raw_transactions[0].has_flag(TransactionFlag.TF_INNER_BATCH_TXN)
        )
        self.assertTrue(
            batch.raw_transactions[1].has_flag(TransactionFlag.TF_INNER_BATCH_TXN)
        )

    def test_too_few_inner_transactions(self):
        payment = Payment(
            account=_ACCOUNT,
            amount="1",
            destination=_DESTINATION,
        )
        with self.assertRaises(XRPLModelException):
            Batch(
                account=_ACCOUNT,
                flags=BatchFlag.TF_ALL_OR_NOTHING,
                raw_transactions=[payment],
            )
