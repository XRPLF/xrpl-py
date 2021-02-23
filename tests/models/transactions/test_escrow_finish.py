from unittest import TestCase

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.transactions import EscrowFinish


class TestEscrowFinish(TestCase):
    def test_fulfillment_set_condition_unset(self):
        fulfillment = "fulfillment"

        transaction_dict = {
            "fulfillment": fulfillment,
        }
        with self.assertRaises(XRPLModelValidationException):
            EscrowFinish.from_dict(transaction_dict)

    def test_condition_set_fulfillment_unset(self):
        condition = "condition"

        transaction_dict = {
            "condition": condition,
        }
        with self.assertRaises(XRPLModelValidationException):
            EscrowFinish.from_dict(transaction_dict)
