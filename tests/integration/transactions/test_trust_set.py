from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import TrustSet, TrustSetFlag
from xrpl.wallet import Wallet


class TestTrustSet(TestCase):
    def test_basic_functionality(self):
        issuer_wallet = Wallet.create()
        response = submit_transaction(
            TrustSet(
                account=WALLET.classic_address,
                sequence=WALLET.next_sequence_num,
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
        WALLET.next_sequence_num += 1
