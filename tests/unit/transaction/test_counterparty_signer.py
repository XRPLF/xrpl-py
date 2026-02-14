"""Unit tests for counterparty signing functions."""

from unittest import TestCase

from xrpl.constants import XRPLException
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanSet, Payment
from xrpl.transaction.counterparty_signer import (
    combine_loanset_counterparty_signers,
    sign_loan_set_by_counterparty,
)
from xrpl.wallet import Wallet


class TestSignLoanSetByCounterpartySingleSign(TestCase):
    """Test single signing of LoanSet by counterparty."""

    def setUp(self):
        self.borrower_wallet = Wallet.from_seed("sEd7FqVHfNZ2UdGAwjssxPev2ujwJoT")

        self.unsigned_loan_set = {
            "TransactionType": "LoanSet",
            "Flags": 0,
            "Sequence": 1702,
            "LastLedgerSequence": 1725,
            "PaymentTotal": 1,
            "LoanBrokerID": (
                "033D9B59DBDC4F48FB6708892E7DB0E8FBF9710C3A181B99D9FAF7B9C82EF077"
            ),
            "Fee": "480",
            "Account": "rpfK3KEEBwXjUXKQnvAs1SbQhVKu7CSkY1",
            "Counterparty": "rp7Tj3Uu1RDrDd1tusge3bVBhUjNvzD19Y",
            "PrincipalRequested": "5000000",
        }

        self.signed_loan_set = {
            **self.unsigned_loan_set,
            "TxnSignature": (
                "1AF5B3118F5F292EDCEAB34A4180792240AF86258C6BC8340D7523D396424F63"
                "B4BD4EAF20DE7C5AA9B472DB86AC36E956DAD02288638E59D90C7A0F6BF6E802"
            ),
            "SigningPubKey": (
                "EDFF8D8C5AC309EAA4F3A0C6D2AAF9A9DFA0724063398110365D4631971F604C4C"
            ),
        }

        self.expected_loan_set = {
            "TransactionType": "LoanSet",
            "Flags": 0,
            "Sequence": 1702,
            "LastLedgerSequence": 1725,
            "PaymentTotal": 1,
            "LoanBrokerID": (
                "033D9B59DBDC4F48FB6708892E7DB0E8FBF9710C3A181B99D9FAF7B9C82EF077"
            ),
            "Fee": "480",
            "SigningPubKey": (
                "EDFF8D8C5AC309EAA4F3A0C6D2AAF9A9DFA0724063398110365D4631971F604C4C"
            ),
            "TxnSignature": (
                "1AF5B3118F5F292EDCEAB34A4180792240AF86258C6BC8340D7523D396424F63"
                "B4BD4EAF20DE7C5AA9B472DB86AC36E956DAD02288638E59D90C7A0F6BF6E802"
            ),
            "Account": "rpfK3KEEBwXjUXKQnvAs1SbQhVKu7CSkY1",
            "Counterparty": "rp7Tj3Uu1RDrDd1tusge3bVBhUjNvzD19Y",
            "PrincipalRequested": "5000000",
            "CounterpartySignature": {
                "SigningPubKey": (
                    "ED1139D765C2C8F175153EE663D2CBE574685D5FCF61A6A33DF7AC72C9903D3F94"
                ),
                "TxnSignature": (
                    "440B839B41834A9292B23A8DB547EA34DC89FC8313056C96812384A860848381"
                    "C4F11867F1092594D3E263DB2433CEB07E2AD312944FF68F2E2EF995ABAE9C05"
                ),
            },
        }

    def test_throws_if_not_signed_by_first_party(self):
        """Transaction must be first signed by first party."""
        loan_set = LoanSet.from_xrpl(self.unsigned_loan_set)
        with self.assertRaises(XRPLException) as context:
            sign_loan_set_by_counterparty(self.borrower_wallet, loan_set)
        self.assertEqual(
            str(context.exception), "Transaction must be first signed by first party."
        )

    def test_throws_if_not_loan_set_transaction(self):
        """Transaction must be a LoanSet transaction."""
        # Create a Payment transaction instead of LoanSet
        payment_tx = Payment(
            account=self.unsigned_loan_set["Account"],
            destination=self.unsigned_loan_set["Counterparty"],
            amount="5000000",
            sequence=self.unsigned_loan_set["Sequence"],
            fee=self.unsigned_loan_set["Fee"],
        )
        with self.assertRaises(XRPLException) as context:
            sign_loan_set_by_counterparty(
                self.borrower_wallet,
                payment_tx,  # type: ignore
            )
        self.assertEqual(
            str(context.exception), "Transaction must be a LoanSet transaction."
        )

    def test_throws_if_already_signed_by_counterparty(self):
        """Transaction is already signed by the counterparty."""
        already_signed_dict = {
            **self.unsigned_loan_set,
            "CounterpartySignature": {
                "SigningPubKey": "",
                "TxnSignature": "",
            },
        }
        loan_set = LoanSet.from_xrpl(already_signed_dict)
        with self.assertRaises(XRPLException) as context:
            sign_loan_set_by_counterparty(self.borrower_wallet, loan_set)
        self.assertEqual(
            str(context.exception),
            "Transaction is already signed by the counterparty.",
        )

    def test_throws_if_validation_fails(self):
        """Transaction must pass validation checks."""
        # Create a LoanSet with invalid interest_rate (exceeds max of 100000)
        # Note: Validation may happen during LoanSet construction or in our function
        invalid_loan_set_dict = {
            **self.signed_loan_set,
            "InterestRate": 200000,  # Invalid: exceeds MAX_INTEREST_RATE
        }
        with self.assertRaises((XRPLException, XRPLModelException)) as context:
            loan_set = LoanSet.from_xrpl(invalid_loan_set_dict)
            sign_loan_set_by_counterparty(self.borrower_wallet, loan_set)
        self.assertIn("interest_rate", str(context.exception).lower())

    def test_single_sign_success(self):
        """Successfully sign LoanSet by counterparty (single signature)."""
        loan_set = LoanSet.from_xrpl(self.signed_loan_set)
        result = sign_loan_set_by_counterparty(self.borrower_wallet, loan_set)
        self.assertEqual(result.tx.to_xrpl(), self.expected_loan_set)


class TestSignLoanSetByCounterpartyMultiSign(TestCase):
    """Test multi-signing of LoanSet by counterparty."""

    def setUp(self):
        self.signer_wallet1 = Wallet.from_seed("sEdSyBUScyy9msTU36wdR68XkskQky5")
        self.signer_wallet2 = Wallet.from_seed("sEdT8LubWzQv3VAx1JQqctv78N28zLA")

        self.unsigned_loan_set = {
            "TransactionType": "LoanSet",
            "Flags": 0,
            "Sequence": 1807,
            "LastLedgerSequence": 1838,
            "PaymentTotal": 1,
            "InterestRate": 0,
            "LoanBrokerID": (
                "D1902EFBFF8C6536322D48B9F3B974AEC29AC826CF6BEA6218C886581A712AFE"
            ),
            "Fee": "720",
            "Account": "rpmFCkiUFiufA3HdLagJCWGbzByaQLJKKJ",
            "Counterparty": "rQnFUSfgnLNA2KzvKUjRX69tbv7WX76UXW",
            "PrincipalRequested": "100000",
        }

        self.signed_loan_set = {
            "TransactionType": "LoanSet",
            "Flags": 0,
            "Sequence": 1807,
            "LastLedgerSequence": 1838,
            "PaymentTotal": 1,
            "InterestRate": 0,
            "LoanBrokerID": (
                "D1902EFBFF8C6536322D48B9F3B974AEC29AC826CF6BEA6218C886581A712AFE"
            ),
            "Fee": "720",
            "SigningPubKey": (
                "EDE7E70883C11FFDEB28A1FEDA20C89352E3FCFEAABFF9EF890A08664E5687ECD2"
            ),
            "TxnSignature": (
                "0438178AF327FC54C42638A4EDB0EB9A701B2D6192388BE8A4C7A61DD82EA451"
                "0D10C0CADAD3D8A7EBC7B08C3F2A50F12F686B47ED2562EE6792434322E94B0E"
            ),
            "Account": "rpmFCkiUFiufA3HdLagJCWGbzByaQLJKKJ",
            "Counterparty": "rQnFUSfgnLNA2KzvKUjRX69tbv7WX76UXW",
            "PrincipalRequested": "100000",
        }

        self.expected_loan_set = {
            "TransactionType": "LoanSet",
            "Flags": 0,
            "Sequence": 1807,
            "LastLedgerSequence": 1838,
            "PaymentTotal": 1,
            "InterestRate": 0,
            "LoanBrokerID": (
                "D1902EFBFF8C6536322D48B9F3B974AEC29AC826CF6BEA6218C886581A712AFE"
            ),
            "Fee": "720",
            "SigningPubKey": (
                "EDE7E70883C11FFDEB28A1FEDA20C89352E3FCFEAABFF9EF890A08664E5687ECD2"
            ),
            "TxnSignature": (
                "0438178AF327FC54C42638A4EDB0EB9A701B2D6192388BE8A4C7A61DD82EA451"
                "0D10C0CADAD3D8A7EBC7B08C3F2A50F12F686B47ED2562EE6792434322E94B0E"
            ),
            "Account": "rpmFCkiUFiufA3HdLagJCWGbzByaQLJKKJ",
            "Counterparty": "rQnFUSfgnLNA2KzvKUjRX69tbv7WX76UXW",
            "PrincipalRequested": "100000",
            "CounterpartySignature": {
                "Signers": [
                    {
                        "Signer": {
                            "SigningPubKey": (
                                "EDD184F5FE58EC1375AB1CF17A3C5A12A8DEE89DD52287"
                                "72D69E28EE37438FE59E"
                            ),
                            "TxnSignature": (
                                "C3A989FFA24CE21AE9E1734653387B34044A82B13F34B7B1175CB2"
                                "0118F9EF904ABEA691E4D3EFFD1EBF63C3B50F29AA89B68AF4A70C"
                                "F74601CD326772D1680E"
                            ),
                            "Account": "rBJMcbqnAaxcUeEPF7WiaoHCtFiTmga7un",
                        },
                    },
                    {
                        "Signer": {
                            "SigningPubKey": (
                                "ED121AF03981F6496E47854955F65FC8763232D74EBF738778895"
                                "14137BB72720A"
                            ),
                            "TxnSignature": (
                                "3A3D91798FCF56289BBF53A97D0CB07CFB5050CFBA05451A1C9A3A"
                                "9E370AE81DCC3134E6CC35579ACA8937F15DF358DAB728054AC17C"
                                "3858177C6947C1E21806"
                            ),
                            "Account": "rKQhhSnRXJyqDq5BFtWG2E6zxAdq6wDyQC",
                        },
                    },
                ],
            },
        }

    def test_multi_sign_and_combine(self):
        """Successfully multi-sign LoanSet by counterparty and combine signatures."""
        loan_set = LoanSet.from_xrpl(self.signed_loan_set)

        # Sign with first signer
        signer1_result = sign_loan_set_by_counterparty(
            self.signer_wallet1,
            loan_set,
            multisign=True,
        )

        # Sign with second signer
        signer2_result = sign_loan_set_by_counterparty(
            self.signer_wallet2,
            loan_set,
            multisign=True,
        )

        # Combine signatures
        combined_result = combine_loanset_counterparty_signers(
            [signer1_result.tx, signer2_result.tx]
        )

        self.assertEqual(combined_result.tx.to_xrpl(), self.expected_loan_set)

    def test_combine_throws_if_empty_list(self):
        """Combining 0 transactions should throw an error."""
        with self.assertRaises(XRPLException) as context:
            combine_loanset_counterparty_signers([])
        self.assertEqual(str(context.exception), "There are 0 transactions to combine.")

    def test_multisign_throws_if_not_signed_by_first_party(self):
        """Transaction must be first signed by first party (multisign mode)."""
        loan_set = LoanSet.from_xrpl(self.unsigned_loan_set)
        with self.assertRaises(XRPLException) as context:
            sign_loan_set_by_counterparty(
                self.signer_wallet1,
                loan_set,
                multisign=True,
            )
        self.assertEqual(
            str(context.exception),
            "Transaction must be first signed by first party.",
        )

    def test_combine_throws_if_transactions_not_identical(self):
        """Combining non-identical transactions should throw an error."""
        loan_set1 = LoanSet.from_xrpl(self.signed_loan_set)

        # Create a different LoanSet transaction (different PrincipalRequested)
        different_loan_set_dict = {
            **self.signed_loan_set,
            "PrincipalRequested": "200000",
        }
        loan_set2 = LoanSet.from_xrpl(different_loan_set_dict)

        # Sign both transactions
        signer1_result = sign_loan_set_by_counterparty(
            self.signer_wallet1,
            loan_set1,
            multisign=True,
        )
        signer2_result = sign_loan_set_by_counterparty(
            self.signer_wallet2,
            loan_set2,
            multisign=True,
        )

        with self.assertRaises(XRPLException) as context:
            combine_loanset_counterparty_signers([signer1_result.tx, signer2_result.tx])
        self.assertEqual(
            str(context.exception),
            "Transactions are not identical.",
        )
