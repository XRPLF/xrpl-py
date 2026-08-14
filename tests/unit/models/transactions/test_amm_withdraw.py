from unittest import TestCase

from xrpl.constants import MPT_ISSUANCE_ID_LENGTH
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.currencies.mpt_currency import MPTCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMWithdraw
from xrpl.models.transactions.amm_withdraw import AMMWithdrawFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ASSET = XRP()
_ASSET2 = IssuedCurrency(currency="ETH", issuer="rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW")
_MPT_ISSUANCE_ID_1 = "00000001A407AF5856CECE4281FED12B7B179B49A4AEF506"
_MPT_ISSUANCE_ID_2 = "00000002A407AF5856CECE4281FED12B7B179B49A4AEF506"
_AMOUNT = "1000"
_LPTOKEN_CURRENCY = "B3813FCAB4EE68B3D0D735D6849465A9113EE048"
_LPTOKEN_ISSUER = "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg"


class TestAMMWithdraw(TestCase):
    def test_tx_valid_lptokenin(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            lp_token_in=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value=_AMOUNT,
            ),
            flags=AMMWithdrawFlag.TF_LP_TOKEN,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount_amount2(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            amount2=IssuedCurrencyAmount(
                currency=_ASSET2.currency, issuer=_ASSET2.issuer, value="500"
            ),
            flags=AMMWithdrawFlag.TF_TWO_ASSET,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount_lptokenin(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            lp_token_in=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value="500",
            ),
            flags=AMMWithdrawFlag.TF_ONE_ASSET_LP_TOKEN,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount_eprice(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            e_price="25",
            flags=AMMWithdrawFlag.TF_LIMIT_LP_TOKEN,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_one_asset_withdraw_all(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            flags=AMMWithdrawFlag.TF_ONE_ASSET_WITHDRAW_ALL,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_withdraw_all(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            flags=AMMWithdrawFlag.TF_WITHDRAW_ALL,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_single_asset_mpt_withdraw(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
            asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
            amount=MPTAmount(
                mpt_issuance_id=_MPT_ISSUANCE_ID_1,
                value="50",
            ),
            flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
        )
        self.assertTrue(tx.is_valid())

    def test_mpt_withdraw_non_hex_characters(self):
        bad_id = "Z" * MPT_ISSUANCE_ID_LENGTH
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
                asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
                flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_withdraw_id_too_short(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH - 1)
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
                asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
                flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_withdraw_id_too_long(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH + 1)
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_1),
                asset2=MPTCurrency(mpt_issuance_id=_MPT_ISSUANCE_ID_2),
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
                flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_undefined_amount_defined_amount2_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=_ASSET,
                asset2=_ASSET2,
                amount2=IssuedCurrencyAmount(
                    currency=_ASSET2.currency, issuer=_ASSET2.issuer, value="500"
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMWithdraw': 'Must set `amount` with `amount2`'}",
        )

    def test_undefined_amount_defined_eprice_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=_ASSET,
                asset2=_ASSET2,
                e_price="25",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMWithdraw': 'Must set `amount` with `e_price`'}",
        )
