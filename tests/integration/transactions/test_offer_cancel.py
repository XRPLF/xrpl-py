from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import OFFER, WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.transactions import OfferCancel

FEE = "3000000"


class TestOfferCancel(TestCase):
    def test_all_fields(self):
        response = submit_transaction(
            OfferCancel(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                offer_sequence=OFFER.result["Sequence"],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        # NOTE: offer cancellations are difficult to test because not
        # specifying an offer ID to cancel is not considered an error.
        #
        # This TX will result in a success essentially as long as it is
        # correctly formatted.
        WALLET.sequence += 1

    def test_high_fee_unauthorized(self):
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # GIVEN a new OfferCancel transaction
            submit_transaction(
                OfferCancel(
                    account=WALLET.classic_address,
                    sequence=WALLET.sequence,
                    offer_sequence=OFFER.result["Sequence"],
                    # WITH fee higher than 2 XRP
                    fee=FEE,
                ),
                WALLET,
                # WITH the default Json RPC Client which doesn't
                # allow more than 2 XRP fee
            )
