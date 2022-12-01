from unittest import TestCase

from xrpl import models
from xrpl.models.exceptions import XRPLModelException
from xrpl.transaction.main import sign
from xrpl.wallet.main import Wallet

# from typing import Iterable

ACCOUNT = "rQUUhraHao4wCqS4MJyzzQP79QE6T9FdeL"
SEED = "snHG27JeogwML83AwTRyvTXxCWteF"

WALLET = Wallet(seed=SEED, sequence=0)


class TestBetterTransactionFlags(TestCase):
    def test_account_set_flags(self):
        actual = models.AccountSet(
            account=ACCOUNT,
            flags=models.AccountSetFlagInterface(
                asf_account_tx_id=True,
                asf_authorized_nftoken_minter=True,
                asf_default_ripple=True,
                asf_deposit_auth=True,
                asf_disable_master=True,
                asf_disallow_xrp=True,
                asf_global_freeze=True,
                asf_no_freeze=True,
                asf_require_auth=True,
                asf_require_dest=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00000005))
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
            nftoken_id="\
                000100001E962F495F07A990F4ED55ACCFEEF365DBAA76B6A048C0A200000007",
            amount="1000000",
            flags=models.NFTokenCreateOfferFlagInterface(
                tf_sell_token=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00000001))
        self.assertTrue(actual.is_valid())
        flags = models.NFTokenCreateOfferFlag
        expected = models.NFTokenCreateOffer(
            account=ACCOUNT,
            nftoken_id="\
                000100001E962F495F07A990F4ED55ACCFEEF365DBAA76B6A048C0A200000007",
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
                tf_burnable=True,
                tf_only_xrp=True,
                tf_transferable=True,
                tf_trustline=True,
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
                tf_fill_or_kill=True,
                tf_passive=True,
                tf_sell=True,
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
                tf_immediate_or_cancel=True,
                tf_passive=True,
                tf_sell=True,
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
                tf_close=True,
                tf_renew=True,
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
        actual = models.Payment(
            account=ACCOUNT,
            destination=dest,
            amount=amnt,
            flags=models.PaymentFlagInterface(
                tf_limit_quality=True,
                tf_no_direct_ripple=True,
                tf_partial_payment=True,
            ),
        )
        self.assertTrue(actual.has_flag(flag=0x00010000))
        self.assertTrue(actual.is_valid())
        flags = models.PaymentFlag
        expected = models.Payment(
            account=ACCOUNT,
            destination=dest,
            amount=amnt,
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

    def test_trust_set_flags(self):
        amnt = models.IssuedCurrencyAmount(
            currency="USD",
            issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
            value="1",
        )
        actual = models.TrustSet(
            account=ACCOUNT,
            limit_amount=amnt,
            flags=models.TrustSetFlagInterface(
                tf_clear_freeze=True,
                tf_clear_no_ripple=True,
                tf_set_auth=True,
                tf_set_freeze=True,
                tf_set_no_ripple=True,
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

    def test_enable_amendment(self):
        amdmt = "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE"
        seq = 21225473
        actual = models.EnableAmendment(
            amendment=amdmt,
            ledger_sequence=seq,
            flags=models.EnableAmendmentFlagInterface(
                tf_got_majority=True,
                tf_lost_majority=True,
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
                        tf_limit_quality=True,
                        tf_no_direct_ripple=True,
                        tf_partial_payment=True,
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
                flags=[65536, models.PaymentFlagInterface(tf_limit_quality=True)],
            )
            sign(transaction=tx, wallet=WALLET)

    def test_transaction_has_no_flags(self):
        actual = models.OfferCancel(
            account=ACCOUNT,
            offer_sequence=6,
            flags=models.PaymentChannelClaimFlagInterface(
                tf_close=True,
            ),
        )
        expected = models.OfferCancel(account=ACCOUNT, offer_sequence=6, flags=0)
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
