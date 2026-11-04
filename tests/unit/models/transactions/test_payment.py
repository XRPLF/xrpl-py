from unittest import TestCase

from xrpl.core.binarycodec import decode
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.path import PathStep
from xrpl.models.transactions import Payment, PaymentFlag
from xrpl.wallet import Wallet

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_XRP_AMOUNT = "10000"
_ISSUED_CURRENCY_AMOUNT = IssuedCurrencyAmount(
    currency="BTC", value="1.002", issuer=_ACCOUNT
)
_DESTINATION = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
_MPT_ID = "00000003430427B80BD2D09D36B70B969E12801065F22308"
_MPT_ISSUER = "rffMEZLzDQPNU6VYbWNkgQBtMz6gCYnMAG"
_MPT_AMOUNT = MPTAmount(mpt_issuance_id=_MPT_ID, value="10")


class TestPayment(TestCase):
    def test_xrp_payment_with_paths(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _XRP_AMOUNT,
            "destination": _DESTINATION,
            "paths": ["random path stuff"],
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_xrp_payment_same_account_destination(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _XRP_AMOUNT,
            "destination": _ACCOUNT,
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_partial_payment_no_sendmax(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _ISSUED_CURRENCY_AMOUNT,
            "destination": _DESTINATION,
            "flags": PaymentFlag.TF_PARTIAL_PAYMENT,
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_deliver_min_no_partial_payment(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _ISSUED_CURRENCY_AMOUNT,
            "destination": _DESTINATION,
            "deliver_min": _ISSUED_CURRENCY_AMOUNT,
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_currency_conversion_no_sendmax(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _ISSUED_CURRENCY_AMOUNT,
            "destination": _ACCOUNT,
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_amount_send_max_xrp_no_partial_payment(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _XRP_AMOUNT,
            "send_max": _XRP_AMOUNT,
            "destination": _DESTINATION,
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_valid_xrp_payment(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _XRP_AMOUNT,
            "destination": _DESTINATION,
        }
        tx = Payment(**transaction_dict)
        self.assertTrue(tx.is_valid())

    def test_valid_issued_currency_payment(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _ISSUED_CURRENCY_AMOUNT,
            "send_max": _XRP_AMOUNT,
            "destination": _DESTINATION,
        }
        tx = Payment(**transaction_dict)
        self.assertTrue(tx.is_valid())

    def test_valid_partial_xrp_payment(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _XRP_AMOUNT,
            "send_max": _XRP_AMOUNT,
            "destination": _DESTINATION,
            "flags": PaymentFlag.TF_PARTIAL_PAYMENT,
        }
        tx = Payment(**transaction_dict)
        self.assertTrue(tx.is_valid())

    def test_destination_wallet(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": _XRP_AMOUNT,
            "send_max": _XRP_AMOUNT,
            "destination": Wallet.create(),
        }
        with self.assertRaises(XRPLModelException):
            Payment(**transaction_dict)

    def test_credentials_array_empty(self):
        with self.assertRaises(XRPLModelException) as err:
            Payment(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
                destination=_DESTINATION,
                credential_ids=[],
            )
        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot be empty.'}",
        )

    def test_credentials_array_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            Payment(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
                destination=_DESTINATION,
                credential_ids=["credential_index_" + str(i) for i in range(9)],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids': 'CredentialIDs list cannot exceed 8 elements.'}",
        )

    def test_credentials_array_duplicates(self):
        with self.assertRaises(XRPLModelException) as err:
            Payment(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
                destination=_DESTINATION,
                credential_ids=["credential_index" for _ in range(5)],
            )

        self.assertEqual(
            err.exception.args[0],
            "{'credential_ids_duplicates': 'CredentialIDs list cannot contain duplicate"
            + " values.'}",
        )

    def test_mpt_payment(self):
        transaction_dict = {
            "account": _ACCOUNT,
            "fee": _FEE,
            "sequence": _SEQUENCE,
            "amount": {
                "mpt_issuance_id": "000004C463C52827307480341125DA0577DEFC38405B0E3E",
                "value": "10",
            },
            "destination": _DESTINATION,
        }
        tx = Payment(**transaction_dict)
        self.assertTrue(tx.is_valid())

    def test_mpt_cross_currency_payment_with_paths(self):
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount=_MPT_AMOUNT,
            send_max=_XRP_AMOUNT,
            paths=[
                [
                    PathStep(currency="BTC", issuer=_ACCOUNT),
                    PathStep(mpt_issuance_id=_MPT_ID),
                ]
            ],
        )
        self.assertTrue(tx.is_valid())
        paths = [
            [
                {"currency": "BTC", "issuer": _ACCOUNT},
                {"mpt_issuance_id": _MPT_ID},
            ]
        ]
        self.assertEqual(tx.to_xrpl()["Paths"], paths)
        # The MPT step used to be encoded as an empty step, truncating the path.
        self.assertEqual(decode(tx.blob())["Paths"], paths)
        self.assertEqual(Payment.from_xrpl(tx.to_xrpl()), tx)

    def test_mpt_payment_with_pathfinding_paths(self):
        # `paths_computed` from ripple_path_find, including the MPT issuer.
        payment_json = {
            "TransactionType": "Payment",
            "Account": _ACCOUNT,
            "Destination": _DESTINATION,
            "Amount": {"mpt_issuance_id": _MPT_ID, "value": "10"},
            "SendMax": _XRP_AMOUNT,
            "Paths": [
                [{"issuer": _MPT_ISSUER, "mpt_issuance_id": _MPT_ID, "type": 96}]
            ],
        }
        tx = Payment.from_xrpl(payment_json)
        self.assertEqual(tx.paths[0][0].mpt_issuance_id, _MPT_ID)
        self.assertEqual(
            decode(tx.blob())["Paths"],
            [[{"mpt_issuance_id": _MPT_ID, "issuer": _MPT_ISSUER}]],
        )

    def test_mpt_partial_payment_with_deliver_min(self):
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount=_MPT_AMOUNT,
            send_max=_ISSUED_CURRENCY_AMOUNT,
            deliver_min=MPTAmount(mpt_issuance_id=_MPT_ID, value="5"),
            flags=PaymentFlag.TF_PARTIAL_PAYMENT,
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(
            decode(tx.blob())["DeliverMin"], {"mpt_issuance_id": _MPT_ID, "value": "5"}
        )

    def test_simple_payment_with_zero_flag(self):
        payment_tx_json = {
            "Account": _ACCOUNT,
            "Destination": _DESTINATION,
            "TransactionType": "Payment",
            "Amount": _XRP_AMOUNT,
            "Fee": _FEE,
            "Flags": 0,
            "Sequence": _SEQUENCE,
        }
        payment_txn = Payment.from_xrpl(payment_tx_json)
        payment = payment_txn.to_xrpl()

        self.assertTrue("Flags" in payment)

    def test_simple_payment_with_zero_flag_direct(self):
        payment_txn = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount=_XRP_AMOUNT,
            fee=_FEE,
            flags=0,
            sequence=_SEQUENCE,
        )
        payment = payment_txn.to_xrpl()

        self.assertTrue("Flags" in payment)

    def test_simple_payment_with_no_flag_direct(self):
        payment_txn = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount=_XRP_AMOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
        )
        payment = payment_txn.to_xrpl()

        self.assertFalse("Flags" in payment)

    def test_simple_payment_with_nonzero_flag(self):
        payment_tx_json = {
            "Account": _ACCOUNT,
            "Destination": _DESTINATION,
            "TransactionType": "Payment",
            "Amount": _XRP_AMOUNT,
            "Fee": _FEE,
            "Flags": 2147483648,
            "Sequence": _SEQUENCE,
        }

        payment_txn = Payment.from_xrpl(payment_tx_json)
        payment = payment_txn.to_xrpl()

        self.assertTrue("Flags" in payment)

    def test_payment_with_valid_domain_id(self):
        tx = Payment(
            account=_ACCOUNT,
            amount=_XRP_AMOUNT,
            destination=_DESTINATION,
            domain_id="ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF123456789"
            "0",
        )
        self.assertTrue(tx.is_valid())

    def test_payment_with_invalid_domain_id(self):
        with self.assertRaises(XRPLModelException) as error:
            Payment(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
                destination=_DESTINATION,
                domain_id="z" * 64,  # invalid (not hex)
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'domain_id must only contain hexadecimal characters.'}",
        )

    def test_payment_with_domain_id_too_short(self):
        with self.assertRaises(XRPLModelException) as error:
            Payment(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
                destination=_DESTINATION,
                domain_id="ABCDEF1234567890",  # only 16 chars, too short
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'domain_id length must be 64 characters.'}",
        )

    def test_payment_with_domain_id_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            Payment(
                account=_ACCOUNT,
                amount=_XRP_AMOUNT,
                destination=_DESTINATION,
                domain_id="A" * 65,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'domain_id': 'domain_id length must be 64 characters.'}",
        )

    def test_sponsor_created_account_flag(self):
        """Payment with tfSponsorCreatedAccount flag."""
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            flags=PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_sponsor_created_account_flag_value(self):
        """Verify flag value is correct."""
        self.assertEqual(PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT, 0x00080000)

    # ------------------------------------------------------------------ #
    #  TF_SPONSOR_CREATED_ACCOUNT mutual-exclusion validation             #
    # ------------------------------------------------------------------ #

    def test_invalid_sponsor_created_account_with_no_ripple_direct(self):
        """TF_SPONSOR_CREATED_ACCOUNT and TF_NO_RIPPLE_DIRECT are mutually exclusive."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1000000",
                flags=(
                    PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT
                    | PaymentFlag.TF_NO_RIPPLE_DIRECT
                ),
            )
        self.assertIn(
            "`TF_SPONSOR_CREATED_ACCOUNT` cannot be combined with "
            "`TF_NO_RIPPLE_DIRECT`.",
            str(cm.exception),
        )

    def test_invalid_sponsor_created_account_with_partial_payment(self):
        """TF_SPONSOR_CREATED_ACCOUNT and TF_PARTIAL_PAYMENT are mutually exclusive."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1000000",
                send_max="2000000",
                flags=(
                    PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT
                    | PaymentFlag.TF_PARTIAL_PAYMENT
                ),
            )
        self.assertIn(
            "`TF_SPONSOR_CREATED_ACCOUNT` cannot be combined with "
            "`TF_PARTIAL_PAYMENT`.",
            str(cm.exception),
        )

    def test_invalid_sponsor_created_account_with_limit_quality(self):
        """TF_SPONSOR_CREATED_ACCOUNT and TF_LIMIT_QUALITY are mutually exclusive."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1000000",
                flags=(
                    PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT
                    | PaymentFlag.TF_LIMIT_QUALITY
                ),
            )
        self.assertIn(
            "`TF_SPONSOR_CREATED_ACCOUNT` cannot be combined with "
            "`TF_LIMIT_QUALITY`.",
            str(cm.exception),
        )

    def test_invalid_sponsor_created_account_with_multiple_incompatible_flags(self):
        """TF_SPONSOR_CREATED_ACCOUNT combined with multiple incompatible flags."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1000000",
                send_max="2000000",
                flags=(
                    PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT
                    | PaymentFlag.TF_NO_RIPPLE_DIRECT
                    | PaymentFlag.TF_PARTIAL_PAYMENT
                ),
            )
        exception_str = str(cm.exception)
        self.assertIn("`TF_NO_RIPPLE_DIRECT`", exception_str)
        self.assertIn("`TF_PARTIAL_PAYMENT`", exception_str)


class TestSponsorCreatedAccountPaymentShape(TestCase):
    """`tfSponsorCreatedAccount` funds a reserve, so it must be plain XRP."""

    _IOU = IssuedCurrencyAmount(currency="USD", issuer=_DESTINATION, value="10")
    _FLAG = PaymentFlag.TF_SPONSOR_CREATED_ACCOUNT

    def test_rejects_issued_currency_amount(self):
        """rippled: `!dstAmount.native()` -> temBAD_AMOUNT."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount=self._IOU,
                send_max=self._IOU,
                flags=self._FLAG,
            )
        self.assertIn("requires an XRP `amount`", str(cm.exception))

    def test_rejects_send_max(self):
        """rippled: `isFieldPresent(sfSendMax)` -> temINVALID."""
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount="1000000",
                send_max=self._IOU,
                flags=self._FLAG,
            )
        self.assertIn("`send_max`", str(cm.exception))

    def test_rejects_paths_even_with_an_issued_amount(self):
        """`paths` is otherwise only rejected for an XRP amount.

        Without a flag-specific rule an issued amount would carry paths straight
        past the model and fail at the server instead.
        """
        with self.assertRaises(XRPLModelException) as cm:
            Payment(
                account=_ACCOUNT,
                destination=_DESTINATION,
                amount=self._IOU,
                send_max=self._IOU,
                flags=self._FLAG,
                paths=[[PathStep(account=_DESTINATION)]],
            )
        self.assertIn("`paths`", str(cm.exception))

    def test_plain_xrp_payment_is_accepted(self):
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000000",
            flags=self._FLAG,
        )
        self.assertTrue(tx.is_valid())
