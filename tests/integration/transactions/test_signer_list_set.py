from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.wallet import Wallet

FEE = "3000000"


class TestSignerListSet(TestCase):
    def test_add_signer(self):
        # sets up another signer for this account
        other_signer = Wallet.create()
        response = submit_transaction(
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

    def test_high_fee_unauthorized(self):
        # sets up another signer for this account
        other_signer = Wallet.create()
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # GIVEN a new SignerListSet transaction
            submit_transaction(
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
                    # WITH the fee higher than 2 XRP
                    fee=FEE,
                ),
                WALLET,
                # WITH the default Json RPC Client which doesn't
                # allow more than 2 XRP fee
            )
