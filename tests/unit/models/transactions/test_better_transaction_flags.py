from unittest import TestCase

from xrpl import models
from xrpl.models.exceptions import XRPLModelException
from xrpl.transaction.main import sign
from xrpl.wallet.main import Wallet

# from typing import Iterable

ACCOUNT = "rQUUhraHao4wCqS4MJyzzQP79QE6T9FdeL"
SEED = "snHG27JeogwML83AwTRyvTXxCWteF"
NFTOKEN_ID = "000100001E962F495F07A990F4ED55ACCFEEF365DBAA76B6A048C0A200000007"

WALLET = Wallet.from_seed(SEED)


class TestBetterTransactionFlags(TestCase):
    def test_account_set_flags(self):
        actual = models.AccountSet(
            account=ACCOUNT,
            flags=models.AccountSetFlagInterface(
                TF_REQUIRE_DEST_TAG=True,
                TF_OPTIONAL_DEST_TAG=True,
                TF_REQUIRE_AUTH=True,
                TF_OPTIONAL_AUTH=True,
                TF_DISALLOW_XRP=True,
                TF_ALLOW_XRP=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.AccountSetFlag
        expected = models.AccountSet(
            account=ACCOUNT,
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_nftoken_create_offer_flags(self):
        actual = models.NFTokenCreateOffer(
            account=ACCOUNT,
            nftoken_id=NFTOKEN_ID,
            amount="1000000",
            flags=models.NFTokenCreateOfferFlagInterface(
                TF_SELL_NFTOKEN=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00000001))
        self.assertTrue(actual.is_valid())
        flags = models.NFTokenCreateOfferFlag
        expected = models.NFTokenCreateOffer(
            account=ACCOUNT,
            nftoken_id=NFTOKEN_ID,
            amount="1000000",
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_nftoken_mint_flags(self):
        actual = models.NFTokenMint(
            account=ACCOUNT,
            nftoken_taxon=0,
            flags=models.NFTokenMintFlagInterface(
                TF_BURNABLE=True,
                TF_ONLY_XRP=True,
                TF_TRANSFERABLE=True,
                TF_TRUSTLINE=True,
                TF_MUTABLE=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00000001))
        self.assertTrue(actual.is_valid())
        flags = models.NFTokenMintFlag
        expected = models.NFTokenMint(
            account=ACCOUNT,
            nftoken_taxon=0,
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_offer_create_fk_flags_tests(self):
        taker_gets = models.IssuedCurrencyAmount(
            currency="USD",
            issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
            value="1",
        )
        taker_pays = "1000000"
        actual = models.OfferCreate(
            account=ACCOUNT,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
            flags=models.OfferCreateFlagInterface(
                TF_FILL_OR_KILL=True,
                TF_PASSIVE=True,
                TF_SELL=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.OfferCreateFlag
        expected = models.OfferCreate(
            account=ACCOUNT,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
            flags=[
                flags.TF_FILL_OR_KILL,
                flags.TF_PASSIVE,
                flags.TF_SELL,
            ],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_offer_create_im_flags_tests(self):
        taker_gets = models.IssuedCurrencyAmount(
            currency="USD",
            issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
            value="1",
        )
        taker_pays = "1000000"
        actual = models.OfferCreate(
            account=ACCOUNT,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
            flags=models.OfferCreateFlagInterface(
                TF_IMMEDIATE_OR_CANCEL=True,
                TF_PASSIVE=True,
                TF_SELL=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.OfferCreateFlag
        expected = models.OfferCreate(
            account=ACCOUNT,
            taker_gets=taker_gets,
            taker_pays=taker_pays,
            flags=[
                flags.TF_IMMEDIATE_OR_CANCEL,
                flags.TF_PASSIVE,
                flags.TF_SELL,
            ],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_payment_channel_claim_flags(self):
        actual = models.PaymentChannelClaim(
            account=ACCOUNT,
            channel="C1AE6DDDEEC05CF2978C0BAD6FE302948E9533691DC749DCDD3B9E5992CA6198",
            flags=models.PaymentChannelClaimFlagInterface(
                TF_CLOSE=True,
                TF_RENEW=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.PaymentChannelClaimFlag
        expected = models.PaymentChannelClaim(
            account=ACCOUNT,
            channel="C1AE6DDDEEC05CF2978C0BAD6FE302948E9533691DC749DCDD3B9E5992CA6198",
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_payment_flags(self):
        dest = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
        amnt = "10000000"
        # TF_SPONSOR_CREATED_ACCOUNT is mutually exclusive with the routing/quality
        # flags below, so it is tested separately in test_payment.py.
        compatible_flags = [
            models.PaymentFlag.TF_LIMIT_QUALITY,
            models.PaymentFlag.TF_NO_RIPPLE_DIRECT,
            models.PaymentFlag.TF_PARTIAL_PAYMENT,
        ]
        actual = models.Payment(
            account=ACCOUNT,
            destination=dest,
            amount=amnt,
            flags=models.PaymentFlagInterface(
                TF_LIMIT_QUALITY=True,
                TF_NO_RIPPLE_DIRECT=True,
                TF_PARTIAL_PAYMENT=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        expected = models.Payment(
            account=ACCOUNT,
            destination=dest,
            amount=amnt,
            flags=compatible_flags,
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_trust_set_flags(self):
        amnt = models.IssuedCurrencyAmount(
            currency="USD",
            issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
            value="1",
        )

        # Note: sets all flags, even invalid combinations since tx is not submitted
        actual = models.TrustSet(
            account=ACCOUNT,
            limit_amount=amnt,
            flags=models.TrustSetFlagInterface(
                TF_CLEAR_FREEZE=True,
                TF_CLEAR_NO_RIPPLE=True,
                TF_SET_AUTH=True,
                TF_SET_FREEZE=True,
                TF_SET_NO_RIPPLE=True,
                TF_SET_DEEP_FREEZE=True,
                TF_CLEAR_DEEP_FREEZE=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.TrustSetFlag
        expected = models.TrustSet(
            account=ACCOUNT,
            limit_amount=amnt,
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_xchain_modify_bridge_flags(self):
        bridge = models.XChainBridge(
            locking_chain_door=ACCOUNT,
            locking_chain_issue=models.XRP(),
            issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            issuing_chain_issue=models.XRP(),
        )
        actual = models.XChainModifyBridge(
            account=ACCOUNT,
            xchain_bridge=bridge,
            flags=models.XChainModifyBridgeFlagInterface(
                TF_CLEAR_ACCOUNT_CREATE_AMOUNT=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.XChainModifyBridgeFlag
        expected = models.XChainModifyBridge(
            account=ACCOUNT,
            xchain_bridge=bridge,
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_enable_amendment(self):
        amdmt = "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE"
        seq = 21225473
        actual = models.EnableAmendment(
            amendment=amdmt,
            ledger_sequence=seq,
            flags=models.EnableAmendmentFlagInterface(
                TF_GOT_MAJORITY=True,
                TF_LOST_MAJORITY=True,
            ),
        )
        flags = models.EnableAmendmentFlag
        expected = models.EnableAmendment(
            amendment=amdmt,
            ledger_sequence=seq,
            flags=[*flags],
        )
        signed_actual = sign(
            transaction=actual,
            wallet=WALLET,
        )
        signed_expected = sign(
            transaction=expected,
            wallet=WALLET,
        )
        self.assertEqual(
            first=signed_actual,
            second=signed_expected,
        )

    def test_no_flags_defined(self):
        try:
            cancel_offer = models.OfferCancel(
                account=ACCOUNT,
                offer_sequence=6,
            )
            sign(
                transaction=cancel_offer,
                wallet=WALLET,
            )
            dest = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
            amnt = "10000000"
            pymnt = models.Payment(
                account=ACCOUNT,
                destination=dest,
                amount=amnt,
            )
            sign(
                transaction=pymnt,
                wallet=WALLET,
            )
        except XRPLModelException:
            self.fail(
                "If no flags are defined 'flags' have to be 0. Txn could not be signed."
            )

    def test_false_flag_definition(self):
        dest = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
        amnt = "10000000"
        with self.assertRaises(XRPLModelException):
            tx = models.Payment(
                account=ACCOUNT,
                destination=dest,
                amount=amnt,
                flags=[
                    models.PaymentFlagInterface(
                        TF_LIMIT_QUALITY=True,
                        TF_NO_RIPPLE_DIRECT=True,
                        TF_PARTIAL_PAYMENT=True,
                    ),
                ],
            )
            sign(transaction=tx, wallet=WALLET)
        with self.assertRaises(XRPLModelException):
            tx = models.Payment(
                account=ACCOUNT,
                destination=dest,
                amount=amnt,
                flags=["1"],
            )
            sign(transaction=tx, wallet=WALLET)
        with self.assertRaises(XRPLModelException):
            tx = models.Payment(
                account=ACCOUNT,
                destination=dest,
                amount=amnt,
                flags=[65536, models.PaymentFlagInterface(TF_LIMIT_QUALITY=True)],
            )
            sign(transaction=tx, wallet=WALLET)

    def test_transaction_has_no_flags(self):
        # A flag that OfferCancel does not define is rejected, not dropped to 0
        with self.assertRaises(XRPLModelException):
            tx = models.OfferCancel(
                account=ACCOUNT,
                offer_sequence=6,
                flags=models.PaymentChannelClaimFlagInterface(
                    TF_CLOSE=True,
                ),
            )
            sign(transaction=tx, wallet=WALLET)

    def test_loan_and_amm_clawback_flags(self):
        loan_set = models.LoanSet(
            account=ACCOUNT,
            loan_broker_id="A" * 64,
            principal_requested="100",
            flags=models.LoanSetFlagInterface(TF_LOAN_OVER_PAYMENT=True),
        )
        self.assertEqual(
            loan_set.to_xrpl()["Flags"], models.LoanSetFlag.TF_LOAN_OVER_PAYMENT
        )
        loan_manage = models.LoanManage(
            account=ACCOUNT,
            loan_id="B" * 64,
            flags=models.LoanManageFlagInterface(TF_LOAN_DEFAULT=True),
        )
        self.assertEqual(
            loan_manage.to_xrpl()["Flags"], models.LoanManageFlag.TF_LOAN_DEFAULT
        )
        amm_clawback = models.AMMClawback(
            account=ACCOUNT,
            holder="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
            asset=models.IssuedCurrency(currency="USD", issuer=ACCOUNT),
            asset2=models.XRP(),
            flags=models.AMMClawbackFlagInterface(TF_CLAW_TWO_ASSETS=True),
        )
        self.assertEqual(
            amm_clawback.to_xrpl()["Flags"], models.AMMClawbackFlag.TF_CLAW_TWO_ASSETS
        )

    def test_global_flag_applies_to_every_transaction_type(self):
        for tx in [
            models.Payment(
                account=ACCOUNT,
                destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
                amount="1",
                flags={"TF_INNER_BATCH_TXN": True},
            ),
            models.AccountDelete(
                account=ACCOUNT,
                destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
                flags={"TF_INNER_BATCH_TXN": True},
            ),
        ]:
            self.assertEqual(
                tx.to_xrpl()["Flags"], models.TransactionFlag.TF_INNER_BATCH_TXN
            )

    def test_unknown_flag_name_set_to_true_raises(self):
        for flags in [{"tfImmediateOrCancel": True}, {"TF_TYPO": True}]:
            with self.assertRaises(XRPLModelException) as error:
                tx = models.OfferCreate(
                    account=ACCOUNT,
                    taker_gets="1000000",
                    taker_pays=models.IssuedCurrencyAmount(
                        currency="USD", issuer=ACCOUNT, value="1"
                    ),
                    flags=flags,
                )
                sign(transaction=tx, wallet=WALLET)
            self.assertIn(
                f"Invalid flag {next(iter(flags))} for OfferCreate.",
                error.exception.args[0],
            )

    def test_unknown_flag_name_set_to_false_is_ignored(self):
        tx = models.OfferCreate(
            account=ACCOUNT,
            taker_gets="1000000",
            taker_pays=models.IssuedCurrencyAmount(
                currency="USD", issuer=ACCOUNT, value="1"
            ),
            flags={"TF_TYPO": False},
        )
        self.assertEqual(tx.to_xrpl()["Flags"], 0)
