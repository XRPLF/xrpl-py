from unittest import TestCase

from xrpl.constants import MPT_ISSUANCE_ID_LENGTH
from xrpl.models.amounts import MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import CheckCreate

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh"
_MPT_ISSUANCE_ID = "00000001A407AF5856CECE4281FED12B7B179B49A4AEF506"


class TestCheckCreate(TestCase):
    def test_tx_valid_with_xrp(self):
        tx = CheckCreate(
            account=_ACCOUNT,
            destination=_DESTINATION,
            send_max="100000000",
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_with_mpt(self):
        tx = CheckCreate(
            account=_ACCOUNT,
            destination=_DESTINATION,
            send_max=MPTAmount(
                mpt_issuance_id=_MPT_ISSUANCE_ID,
                value="50",
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_with_mpt_and_optional_fields(self):
        tx = CheckCreate(
            account=_ACCOUNT,
            destination=_DESTINATION,
            send_max=MPTAmount(
                mpt_issuance_id=_MPT_ISSUANCE_ID,
                value="50",
            ),
            destination_tag=1,
            expiration=970113521,
            invoice_id=(
                "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B"
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_mpt_send_max_non_hex_characters(self):
        bad_id = "Z" * MPT_ISSUANCE_ID_LENGTH
        with self.assertRaises(XRPLModelException) as error:
            CheckCreate(
                account=_ACCOUNT,
                destination=_DESTINATION,
                send_max=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_send_max_id_too_short(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH - 1)
        with self.assertRaises(XRPLModelException) as error:
            CheckCreate(
                account=_ACCOUNT,
                destination=_DESTINATION,
                send_max=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_send_max_id_too_long(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH + 1)
        with self.assertRaises(XRPLModelException) as error:
            CheckCreate(
                account=_ACCOUNT,
                destination=_DESTINATION,
                send_max=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )
