from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import FEE, WALLET
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.wallet import Wallet


class TestSignerListSet(TestCase):
    def test_add_signer(self):
        # sets up another signer for this account
        other_signer = Wallet.create()
        response = submit_transaction(
            SignerListSet(
                account=WALLET.classic_address,
                sequence=WALLET.next_sequence_num,
                fee=FEE,
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
        WALLET.next_sequence_num += 1
