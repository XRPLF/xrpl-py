try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction, submit_transaction_async
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCancel

ACCOUNT = WALLET.classic_address
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
OFFER_SEQUENCE = 7


class TestEscrowCancel(IsolatedAsyncioTestCase):
    def test_all_fields_sync(self):
        escrow_cancel = EscrowCancel(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
        )
        response = submit_transaction(escrow_cancel, WALLET)
        # Actual engine_result is `tecNO_TARGET since OWNER account doesn't exist
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

    async def test_all_fields_async(self):
        escrow_cancel = EscrowCancel(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
        )
        response = await submit_transaction_async(escrow_cancel, WALLET)
        # Actual engine_result is `tecNO_TARGET since OWNER account doesn't exist
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
