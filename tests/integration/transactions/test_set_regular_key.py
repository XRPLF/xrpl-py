from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.transactions import SetRegularKey
from xrpl.wallet import Wallet

FEE = "3000000"


class TestSetRegularKey(TestCase):
    def test_all_fields(self):
        regular_key = Wallet.create().classic_address
        response = submit_transaction(
            SetRegularKey(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                regular_key=regular_key,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1

    def test_fee_higher_than_two_xrp_forbidden(self):
        regular_key = Wallet.create().classic_address
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # GIVEN a new SetRegularKey transaction
            submit_transaction(
                SetRegularKey(
                    account=WALLET.classic_address,
                    sequence=WALLET.sequence,
                    regular_key=regular_key,
                    # WITH the fee higher than 2 XRP
                    fee=FEE,
                ),
                WALLET,
                # WITH the default Json RPC Client which doesn't
                # allow more than 2 XRP fee
            )
