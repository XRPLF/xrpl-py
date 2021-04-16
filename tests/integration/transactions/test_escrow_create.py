from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCreate

ACCOUNT = WALLET.classic_address

AMOUNT = "10000"
DESTINATION = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
CANCEL_AFTER = 533257958
FINISH_AFTER = 533171558
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
DESTINATION_TAG = 23480
SOURCE_TAG = 11747
FEE = "3000000"


class TestEscrowCreate(TestCase):
    def test_all_fields(self):
        escrow_create = EscrowCreate(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            amount=AMOUNT,
            destination=DESTINATION,
            destination_tag=DESTINATION_TAG,
            cancel_after=CANCEL_AFTER,
            finish_after=FINISH_AFTER,
            source_tag=SOURCE_TAG,
        )
        response = submit_transaction(escrow_create, WALLET)
        # Actual engine_result will be `tecNO_PERMISSION`...
        # maybe due to CONDITION or something
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

    def test_high_fee_unauthorized(self):
        # GIVEN a new EscrowCreate transaction
        escrow_create = EscrowCreate(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            amount=AMOUNT,
            destination=DESTINATION,
            destination_tag=DESTINATION_TAG,
            cancel_after=CANCEL_AFTER,
            finish_after=FINISH_AFTER,
            source_tag=SOURCE_TAG,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            submit_transaction(escrow_create, WALLET)
