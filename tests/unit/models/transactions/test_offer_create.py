from unittest import TestCase

from xrpl.constants import MPT_ISSUANCE_ID_LENGTH
from xrpl.models.amounts import MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.offer_create import OfferCreate, OfferCreateFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_TAKER_GETS = {
    "currency": "USD",
    "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "value": "100",
}
_TAKER_GETS_MPT = {
    "mpt_issuance_id": "000004C463C52827307480341125DA0577DEFC38405B0E3E",
    "value": "100",
}
_TAKER_PAYS = {
    "currency": "EUR",
    "issuer": "rJ4EpEPTDR88GpXvix3Y1djATCsDn41ixp",
    "value": "90",
}
_TAKER_PAYS_MPT = {
    "mpt_issuance_id": "000004C463C52827307480341125DA0577DEFC38405BABCD",
    "value": "30",
}


class TestOfferCreate(TestCase):
    def test_offer_create_valid(self):
        tx = OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS,
            taker_pays=_TAKER_PAYS,
        )
        self.assertTrue(tx.is_valid())

    def test_offer_create_valid_taker_pays_mpt(self):
        tx = OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS,
            taker_pays=_TAKER_PAYS_MPT,
        )
        self.assertTrue(tx.is_valid())

    def test_offer_create_valid_taker_gets_mpt(self):
        tx = OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS_MPT,
            taker_pays=_TAKER_PAYS,
        )
        self.assertTrue(tx.is_valid())

    def test_offer_create_valid_mpt_on_both_sides(self):
        tx = OfferCreate(
            account=_ACCOUNT,
            taker_gets=_TAKER_GETS_MPT,
            taker_pays=_TAKER_PAYS_MPT,
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

    def test_offer_create_with_domain_id_too_short(self):
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

    def test_offer_create_with_domain_id_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=_TAKER_GETS,
                taker_pays=_TAKER_PAYS,
                domain_id="A" * 65,  # Invalid: too long
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'domain_id length must be 64 characters.'}",
        )

    def test_mpt_taker_gets_non_hex_characters(self):
        bad_id = "Z" * MPT_ISSUANCE_ID_LENGTH
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="100",
                ),
                taker_pays=_TAKER_PAYS,
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_taker_gets_id_too_short(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH - 1)
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="100",
                ),
                taker_pays=_TAKER_PAYS,
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_taker_gets_id_too_long(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH + 1)
        with self.assertRaises(XRPLModelException) as error:
            OfferCreate(
                account=_ACCOUNT,
                taker_gets=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="100",
                ),
                taker_pays=_TAKER_PAYS,
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )
