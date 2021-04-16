from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCash

ACCOUNT = WALLET.classic_address
CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
AMOUNT = "100000000"
DELIVER_MIN = "100000000"

FEE = "3000000"


class TestCheckCreate(TestCase):
    def test_required_fields_with_amount(self):
        check_cash = CheckCash(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            check_id=CHECK_ID,
            amount=AMOUNT,
        )
        response = submit_transaction(check_cash, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # Getting `tecNO_ENTRY` codes because using a non-existent check ID
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")
        WALLET.sequence += 1

    def test_required_fields_with_deliver_min(self):
        check_cash = CheckCash(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            check_id=CHECK_ID,
            deliver_min=DELIVER_MIN,
        )
        response = submit_transaction(check_cash, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")
        WALLET.sequence += 1

    def test_high_fee_unauthorized(self):
        # GIVEN a new CheckCash transaction
        check_cash = CheckCash(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            check_id=CHECK_ID,
            deliver_min=DELIVER_MIN,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            submit_transaction(check_cash, WALLET)
