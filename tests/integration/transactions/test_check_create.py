from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCreate

ACCOUNT = WALLET.classic_address
DESTINATION_TAG = 1
SENDMAX = "100000000"
EXPIRATION = 970113521
INVOICE_ID = "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B"
FEE = "3000000"


class TestCheckCreate(TestCase):
    def test_all_fields(self):
        check_create = CheckCreate(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            send_max=SENDMAX,
            expiration=EXPIRATION,
            invoice_id=INVOICE_ID,
        )
        response = submit_transaction(check_create, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        WALLET.sequence += 1

    def test_high_fee_unauthorized(self):
        # GIVEN a new CheckCreate transaction
        check_create = CheckCreate(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            send_max=SENDMAX,
            expiration=EXPIRATION,
            invoice_id=INVOICE_ID,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # WITH the default Json RPC Client which doesn't
            # allow more than 2 XRP fee
            submit_transaction(check_create, WALLET)
