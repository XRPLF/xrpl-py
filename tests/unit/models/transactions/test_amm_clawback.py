from unittest import TestCase

from xrpl.constants import MPT_ISSUANCE_ID_LENGTH
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.currencies.mpt_currency import MPTCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMClawback
from xrpl.models.transactions.amm_clawback import AMMClawbackFlag

_ISSUER_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_HOLDER_ACCOUNT = "rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh"
_MPT_ISSUANCE_ID_1 = "00000001A407AF5856CECE4281FED12B7B179B49A4AEF506"
_MPT_ISSUANCE_ID_2 = "00000002A407AF5856CECE4281FED12B7B179B49A4AEF506"
_ASSET2 = XRP()
_INVALID_ASSET = IssuedCurrency(
    currency="ETH", issuer="rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW"
)
_VALID_ASSET = IssuedCurrency(currency="ETH", issuer=_ISSUER_ACCOUNT)
_HOLDER_ACCOUNT = "rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh"


class TestAMMClawback(TestCase):
    def test_identical_issuer_holder_wallets(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_ISSUER_ACCOUNT,
                asset=_VALID_ASSET,
                asset2=_ASSET2,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Issuer and holder wallets must be distinct.'}",
        )

    def test_incorrect_asset_issuer(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=_INVALID_ASSET,
                asset2=_ASSET2,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Asset.issuer and AMMClawback transaction sender must be "
            + "identical.'}",
        )

    def test_incorrect_asset_amount(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=_VALID_ASSET,
                asset2=_ASSET2,
                amount=IssuedCurrencyAmount(
                    currency="BTC",
                    issuer="rfpFv97Dwu89FTyUwPjtpZBbuZxTqqgTmH",
                    value="100",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Amount.issuer and Amount.currency must match "
            + "corresponding Asset fields.'}",
        )

    def test_valid_txn(self):
        txn = AMMClawback(
            account=_ISSUER_ACCOUNT,
            holder=_HOLDER_ACCOUNT,
            asset=_VALID_ASSET,
            asset2=_ASSET2,
            flags=AMMClawbackFlag.TF_CLAW_TWO_ASSETS,
        )
        self.assertTrue(txn.is_valid())

    def test_valid_mpt_clawback(self):
        txn = AMMClawback(
            account=_ISSUER_ACCOUNT,
            holder=_HOLDER_ACCOUNT,
            asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
            asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
            amount=MPTAmount(
                mpt_issuance_id=_MPT_ISSUANCE_ID_1,
                value="10",
            ),
        )
        self.assertTrue(txn.is_valid())

    def test_valid_mpt_clawback_without_amount(self):
        txn = AMMClawback(
            account=_ISSUER_ACCOUNT,
            holder=_HOLDER_ACCOUNT,
            asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
            asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
        )
        self.assertTrue(txn.is_valid())

    def test_mpt_clawback_non_hex_characters(self):
        bad_id = "Z" * MPT_ISSUANCE_ID_LENGTH
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
                asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="10",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_clawback_id_too_short(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH - 1)
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
                asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="10",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_clawback_id_too_long(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH + 1)
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
                asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="10",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )
