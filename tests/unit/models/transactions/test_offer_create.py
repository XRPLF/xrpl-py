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
            domain_id="ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF123456789"
            "0",
        )

    def test_offer_create_valid_domain_id(self):
        """
        A valid 64-character hex domain_id should pass validation.
        """
        tx = OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS,
            taker_pays=_TAKER_PAYS,
            domain_id="a" * 64,
        )
        self.assertTrue(tx.is_valid())

    def test_offer_create_invalid_domain_id_not_hex(self):
        """
        A domain_id must be a 64-character hex string.
        If domain_id contains non-hex characters, XRPLModelException is raised.
        """
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=_TAKER_GETS,
                taker_pays=_TAKER_PAYS,
                domain_id="z" * 64,  # Invalid: not hex
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'domain_id must only contain hexadecimal characters.'}",
        )

    def test_offer_create_invalid_domain_id_length(self):
        """
        A domain_id must be a 64-character hex string.
        If domain_id is too short/long, XRPLModelException is raised.
        """
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=_TAKER_GETS,
                taker_pays=_TAKER_PAYS,
                domain_id="12345",  # Invalid: too short
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'domain_id length must be 64 characters.'}",
        )
