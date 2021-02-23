from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions import EscrowCreate


class TestEscrowCreate(TestCase):
    def test_final_after_less_than_cancel_after(self):
        cancel_after = 2
        finish_after = 1

        transaction_dict = {
            "cancel_after": cancel_after,
            "finish_after": finish_after,
        }
        with self.assertRaises(XRPLModelValidationException):
            EscrowCreate.from_dict(transaction_dict)
