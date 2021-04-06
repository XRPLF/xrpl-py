from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import OFFER, OFFER_OBJECT, WALLET
from xrpl.transaction import safe_sign_and_autofill_transaction


class TestOfferCreate(TestCase):
    def test_basic_functionality(self):
        signed_offer = safe_sign_and_autofill_transaction(
            OFFER_OBJECT, WALLET, JSON_RPC_CLIENT
        )
        print(signed_offer)
        print(signed_offer.get_hash())
        print(OFFER.result["hash"])
