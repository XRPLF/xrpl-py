from unittest import TestCase

from xrpl.core.binarycodec import decode
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.currencies import XRP, IssuedCurrency, MPTCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMClawback
from xrpl.models.transactions.amm_clawback import AMMClawbackFlag

_ISSUER_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ASSET2 = XRP()
_INVALID_ASSET = IssuedCurrency(
    currency="ETH", issuer="rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW"
)
_VALID_ASSET = IssuedCurrency(currency="ETH", issuer=_ISSUER_ACCOUNT)
_HOLDER_ACCOUNT = "rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh"
# The issuer of an MPT is encoded in its MPTokenIssuanceID.
_MPT_ISSUER = "rffMEZLzDQPNU6VYbWNkgQBtMz6gCYnMAG"
_MPT_ID = "00000003430427B80BD2D09D36B70B969E12801065F22308"
_OTHER_MPT_ID = "00000004430427B80BD2D09D36B70B969E12801065F22308"
_MPT_ASSET = MPTCurrency(mpt_issuance_id=_MPT_ID)


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

    def test_valid_mpt_txn(self):
        txn = AMMClawback(
            account=_MPT_ISSUER,
            holder=_HOLDER_ACCOUNT,
            asset=_MPT_ASSET,
            asset2=MPTCurrency(mpt_issuance_id=_OTHER_MPT_ID),
            amount=MPTAmount(mpt_issuance_id=_MPT_ID.lower(), value="100"),
            flags=AMMClawbackFlag.TF_CLAW_TWO_ASSETS,
        )
        self.assertTrue(txn.is_valid())
        self.assertEqual(AMMClawback.from_xrpl(txn.to_xrpl()), txn)
        self.assertEqual(decode(txn.blob())["Asset"], {"mpt_issuance_id": _MPT_ID})

    def test_mpt_asset_not_issued_by_account(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=_MPT_ASSET,
                asset2=_ASSET2,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Asset.issuer and AMMClawback transaction sender must be "
            + "identical.'}",
        )

    def test_mpt_amount_mismatch(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_MPT_ISSUER,
                holder=_HOLDER_ACCOUNT,
                asset=_MPT_ASSET,
                asset2=_ASSET2,
                amount=MPTAmount(mpt_issuance_id=_OTHER_MPT_ID, value="100"),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Amount.mpt_issuance_id must match "
            + "Asset.mpt_issuance_id.'}",
        )

    def test_mpt_asset_with_issued_currency_amount(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_MPT_ISSUER,
                holder=_HOLDER_ACCOUNT,
                asset=_MPT_ASSET,
                asset2=_ASSET2,
                amount=IssuedCurrencyAmount(
                    currency="ETH", issuer=_MPT_ISSUER, value="100"
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Amount.mpt_issuance_id must match "
            + "Asset.mpt_issuance_id.'}",
        )

    def test_issued_currency_asset_with_mpt_amount(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=_VALID_ASSET,
                asset2=_ASSET2,
                amount=MPTAmount(mpt_issuance_id=_MPT_ID, value="100"),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMClawback': 'Amount.issuer and Amount.currency must match "
            + "corresponding Asset fields.'}",
        )

    def test_xrp_asset(self):
        with self.assertRaises(XRPLModelException):
            AMMClawback(
                account=_ISSUER_ACCOUNT,
                holder=_HOLDER_ACCOUNT,
                asset=XRP(),
                asset2=_VALID_ASSET,
            )
