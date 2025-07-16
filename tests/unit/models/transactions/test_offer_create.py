from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.offer_create import OfferCreate, OfferCreateFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_TAKER_GETS = {
    "currency": "USD",
    "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "value": "100",
}
_TAKER_PAYS = {
    "currency": "EUR",
    "issuer": "rJ4EpEPTDR88GpXvix3Y1djATCsDn41ixp",
    "value": "90",
}


class TestOfferCreate(TestCase):
    def test_offer_create_valid(self):
        tx = OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS,
            taker_pays=_TAKER_PAYS,
        )
        self.assertTrue(tx.is_valid())

    def test_offer_create_hybrid_flag_without_domain_id(self):
        """
        A hybrid offer (tfHybrid flag set) should require domain_id.
        If domain_id is missing, is_valid() should be False and an error should be
        present.
        """
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=_TAKER_GETS,
                taker_pays=_TAKER_PAYS,
                flags=OfferCreateFlag.TF_HYBRID,
                domain_id=None,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'Hybrid offer (tfHybrid flag) requires domain_id to be set.'"
            "}",
        )

    def test_offer_create_hybrid_flag_with_domain_id(self):
        """
        A hybrid offer (tfHybrid flag set) with domain_id should pass validation.
        """
        OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS,
            taker_pays=_TAKER_PAYS,
            flags=OfferCreateFlag.TF_HYBRID,
            domain_id="ABCDEF1234567890",
        )
