from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCancel

ACCOUNT = WALLET.classic_address
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
OFFER_SEQUENCE = 7


class TestEscrowCancel(TestCase):
    def test_all_fields(self):
        escrow_cancel = EscrowCancel(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
        )
        response = submit_transaction(escrow_cancel, WALLET)
        # Actual engine_result is `tecNO_TARGET since OWNER account doesn't exist
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
