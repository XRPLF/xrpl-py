from unittest import IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction, submit_transaction_async
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.wallet import Wallet


class TestTrustSet(IsolatedAsyncioTestCase):
    def test_basic_functionality_sync(self):
        issuer_wallet = Wallet.create()
        response = submit_transaction(
            TrustSet(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1

    async def test_basic_functionality_async(self):
        issuer_wallet = Wallet.create()
        response = await submit_transaction_async(
            TrustSet(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                flags=TrustSetFlag.TF_SET_NO_RIPPLE,
                limit_amount=IssuedCurrencyAmount(
                    issuer=issuer_wallet.classic_address,
                    currency="USD",
                    value="100",
                ),
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
