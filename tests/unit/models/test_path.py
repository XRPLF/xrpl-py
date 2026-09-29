from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.path import PathStep

_MPT_ID = "00000003430427B80BD2D09D36B70B969E12801065F22308"
_MPT_ISSUER = "rffMEZLzDQPNU6VYbWNkgQBtMz6gCYnMAG"
_MPT_ISSUER_HEX = "430427B80BD2D09D36B70B969E12801065F22308"
_OTHER_ACCOUNT = "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B"


class TestPathStep(TestCase):
    def test_valid_mpt_step(self):
        self.assertTrue(PathStep(mpt_issuance_id=_MPT_ID).is_valid())

    def test_valid_mpt_step_with_issuer(self):
        # rippled's pathfinder returns MPT steps in this form (type 0x60).
        step = PathStep(mpt_issuance_id=_MPT_ID, issuer=_MPT_ISSUER, type=96)
        self.assertTrue(step.is_valid())

    def test_valid_mpt_step_with_hex_issuer(self):
        step = PathStep(mpt_issuance_id=_MPT_ID, issuer=_MPT_ISSUER_HEX.lower())
        self.assertTrue(step.is_valid())

    def test_mpt_step_with_wrong_issuer(self):
        with self.assertRaises(XRPLModelException) as error:
            PathStep(mpt_issuance_id=_MPT_ID, issuer=_OTHER_ACCOUNT)
        self.assertEqual(
            error.exception.args[0],
            "{'issuer': 'Issuer must match the issuer encoded in mpt_issuance_id'}",
        )

    def test_mpt_step_with_currency(self):
        with self.assertRaises(XRPLModelException) as error:
            PathStep(mpt_issuance_id=_MPT_ID, currency="USD")
        self.assertEqual(
            error.exception.args[0],
            "{'mpt_issuance_id': 'Cannot set both currency and mpt_issuance_id'}",
        )

    def test_mpt_step_with_account(self):
        with self.assertRaises(XRPLModelException) as error:
            PathStep(mpt_issuance_id=_MPT_ID, account=_OTHER_ACCOUNT)
        self.assertEqual(
            error.exception.args[0],
            "{'account': 'Cannot set account if mpt_issuance_id is set'}",
        )

    def test_invalid_mpt_issuance_id(self):
        for invalid in (_MPT_ID[:-2], _MPT_ID[:-1] + "G"):
            with self.subTest(mpt_issuance_id=invalid):
                with self.assertRaises(XRPLModelException) as error:
                    PathStep(mpt_issuance_id=invalid, issuer=_MPT_ISSUER)
                self.assertEqual(
                    error.exception.args[0],
                    f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {invalid}'}}",
                )

    def test_mpt_step_from_dict(self):
        step_dict = {"issuer": _MPT_ISSUER, "mpt_issuance_id": _MPT_ID, "type": 96}
        step = PathStep.from_dict(step_dict)
        self.assertEqual(step.mpt_issuance_id, _MPT_ID)
        self.assertEqual(step.to_dict(), step_dict)

    def test_issued_currency_steps_unchanged(self):
        self.assertTrue(PathStep(currency="USD", issuer=_OTHER_ACCOUNT).is_valid())
        self.assertTrue(PathStep(currency="XRP").is_valid())
        self.assertTrue(PathStep(account=_OTHER_ACCOUNT).is_valid())
        with self.assertRaises(XRPLModelException):
            PathStep(currency="XRP", issuer=_OTHER_ACCOUNT)
        with self.assertRaises(XRPLModelException):
            PathStep(account=_OTHER_ACCOUNT, currency="USD")
