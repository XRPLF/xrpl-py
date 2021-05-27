try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.wallet import Wallet


class TestSignerListSet(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_add_signer(self, client):
        # sets up another signer for this account
        other_signer = Wallet.create()
        response = await submit_transaction_async(
            SignerListSet(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                signer_quorum=1,
                signer_entries=[
                    SignerEntry(
                        account=other_signer.classic_address,
                        signer_weight=1,
                    ),
                ],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
