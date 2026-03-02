from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.path import PathStep

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ISSUER = "rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW"
_MPT_ID = "00000001A407AF5856CECE4281FED12B7B179B49A4AEF506"


class TestPathStepMPT(TestCase):
    # --- valid cases ---

    def test_valid_mpt_issuance_id_only(self):
        step = PathStep(mpt_issuance_id=_MPT_ID)
        self.assertTrue(step.is_valid())

    def test_valid_account_only(self):
        step = PathStep(account=_ACCOUNT)
        self.assertTrue(step.is_valid())

    # --- account + mpt_issuance_id ---

    def test_account_with_mpt_issuance_id(self):
        with self.assertRaises(XRPLModelException) as ctx:
            PathStep(account=_ACCOUNT, mpt_issuance_id=_MPT_ID)
        self.assertIn(
            "Cannot set account if mpt_issuance_id is specified",
            ctx.exception.args[0],
        )

    # --- currency + mpt_issuance_id ---

    def test_currency_with_mpt_issuance_id(self):
        with self.assertRaises(XRPLModelException) as ctx:
            PathStep(currency="USD", mpt_issuance_id=_MPT_ID)
        self.assertIn(
            "Cannot set both currency and mpt_issuance_id",
            ctx.exception.args[0],
        )

    # --- mpt_issuance_id + currency (from mpt validator) ---

    def test_mpt_issuance_id_with_currency(self):
        """Same combo as above, but verifies the mpt_issuance_id validator's message."""
        with self.assertRaises(XRPLModelException) as ctx:
            PathStep(mpt_issuance_id=_MPT_ID, currency="USD")
        self.assertIn(
            "Cannot set both mpt_issuance_id and currency",
            ctx.exception.args[0],
        )

    # --- mpt_issuance_id + account (from mpt validator) ---

    def test_mpt_issuance_id_with_account(self):
        with self.assertRaises(XRPLModelException) as ctx:
            PathStep(mpt_issuance_id=_MPT_ID, account=_ACCOUNT)
        self.assertIn(
            "Cannot set both mpt_issuance_id and account",
            ctx.exception.args[0],
        )
