from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, submit_transaction
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.transactions import PaymentChannelClaim

FEE = "3000000"


class TestPaymentChannelClaim(TestCase):
    def test_receiver_claim(self):
        response = submit_transaction(
            PaymentChannelClaim(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                channel=PAYMENT_CHANNEL.result["hash"],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1

    def test_receiver_claim_with_high_fee_unauthorized(self):
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            submit_transaction(
                # GIVEN a new PaymentChannelClaim transaction
                PaymentChannelClaim(
                    account=WALLET.classic_address,
                    sequence=WALLET.sequence,
                    # WITH the fee higher than 2 XRP
                    fee=FEE,
                    channel=PAYMENT_CHANNEL.result["hash"],
                ),
                WALLET,
            )

    def test_receiver_claim_with_high_fee_authorized(self):
        # GIVEN a new PaymentChannelClaim transaction
        response = submit_transaction(
            PaymentChannelClaim(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                # WITH the fee higher than 2 XRP
                fee=FEE,
                channel=PAYMENT_CHANNEL.result["hash"],
            ),
            WALLET,
            JSON_RPC_CLIENT,
            # WITHOUT checking the fee value
            False,
        )
        # THEN we expect a successful response
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
