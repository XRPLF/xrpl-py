from unittest import TestCase
from xrpl.models.exceptions import XRPLModelException

from xrpl.models.transactions.pseudo_transactions import (
    EnableAmendment,
    SetFee,
    UNLModify,
)
from xrpl.models.transactions.pseudo_transactions.pseudo_transaction import (
    PseudoTransaction,
)
from xrpl.models.transactions.transaction import Transaction

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048


class TestPseudoTransactions(TestCase):
    def test_from_xrpl_enable_amendment(self):
        amendment = "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE"
        ledger_sequence = 21225473
        amendment_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "Amendment": amendment,
            "Fee": "0",
            "LedgerSequence": ledger_sequence,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "EnableAmendment",
        }
        expected = EnableAmendment(
            amendment=amendment,
            ledger_sequence=ledger_sequence,
        )
        actual = PseudoTransaction.from_xrpl(amendment_dict)
        self.assertEqual(actual, expected)
        full_dict = {**amendment_dict, "Flags": 0, "TxnSignature": ""}
        self.assertEqual(actual.to_xrpl(), full_dict)

    def test_from_xrpl_set_fee_pre_amendment(self):
        reference_fee_units = 10
        reserve_base = 20000000
        reserve_increment = 5000000
        base_fee = "000000000000000A"
        set_fee_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "BaseFee": base_fee,
            "Fee": "0",
            "ReferenceFeeUnits": reference_fee_units,
            "ReserveBase": reserve_base,
            "ReserveIncrement": reserve_increment,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "SetFee",
        }
        expected = SetFee(
            reference_fee_units=reference_fee_units,
            reserve_base=reserve_base,
            reserve_increment=reserve_increment,
            base_fee=base_fee,
        )
        actual = Transaction.from_xrpl(set_fee_dict)
        self.assertEqual(actual, expected)
        full_dict = {**set_fee_dict, "Flags": 0, "TxnSignature": ""}
        self.assertEqual(actual.to_xrpl(), full_dict)

    def test_set_fee_throws_with_missing_pre_amendment_parameters(self):
        # reference_fee_units = 10 - Removed as part of this test.
        reserve_base = 20000000
        reserve_increment = 5000000
        base_fee = "000000000000000A"
        set_fee_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "BaseFee": base_fee,
            "Fee": "0",
            # "ReferenceFeeUnits": reference_fee_units, - Removed as part of this test.
            "ReserveBase": reserve_base,
            "ReserveIncrement": reserve_increment,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "SetFee",
        }
        with self.assertRaises(XRPLModelException):
            SetFee(
                # reference_fee_units - Removed as part of this test.
                reserve_base=reserve_base,
                reserve_increment=reserve_increment,
                base_fee=base_fee,
            )
        with self.assertRaises(XRPLModelException):
            Transaction.from_xrpl(set_fee_dict)

    def test_set_fee_throws_with_missing_post_amendment_parameters(self):
        # reserve_base_drops = "20000000" - Removed as part of this test.
        reserve_increment_drops = "5000000"
        base_fee_drops = "000000000000000A"
        set_fee_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "BaseFeeDrops": base_fee_drops,
            "Fee": "0",
            # "ReserveBaseDrops": reserve_base_drops, - Removed as part of this test.
            "ReserveIncrementDrops": reserve_increment_drops,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "SetFee",
        }
        with self.assertRaises(XRPLModelException):
            SetFee(
                # reserve_base_drops=reserve_base_drops, - Removed as part of this test.
                reserve_increment_drops=reserve_increment_drops,
                base_fee_drops=base_fee_drops,
            )
        with self.assertRaises(XRPLModelException):
            Transaction.from_xrpl(set_fee_dict)

    def test_from_xrpl_set_fee_post_amendment(self):
        reserve_base_drops = "20000000"
        reserve_increment_drops = "5000000"
        base_fee_drops = "000000000000000A"
        set_fee_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "BaseFeeDrops": base_fee_drops,
            "Fee": "0",
            "ReserveBaseDrops": reserve_base_drops,
            "ReserveIncrementDrops": reserve_increment_drops,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "SetFee",
        }
        expected = SetFee(
            reserve_base_drops=reserve_base_drops,
            reserve_increment_drops=reserve_increment_drops,
            base_fee_drops=base_fee_drops,
        )
        actual = Transaction.from_xrpl(set_fee_dict)
        self.assertEqual(actual, expected)
        full_dict = {**set_fee_dict, "Flags": 0, "TxnSignature": ""}
        self.assertEqual(actual.to_xrpl(), full_dict)

    def test_set_fee_disallows_mixing_fields_from_pre_and_post_amendment(
        self,
    ):
        reserve_base_drops = "20000000"
        reserve_increment_drops = "5000000"
        base_fee = "000000000000000A"
        set_fee_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "BaseFeeDrops": base_fee,
            "Fee": "0",
            "ReserveBase": int(reserve_base_drops),  # Pre-XRPFees amendment
            "ReserveBaseDrops": str(reserve_base_drops),  # Post-XRPFees amendment
            "ReserveIncrementDrops": reserve_increment_drops,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "SetFee",
        }
        with self.assertRaises(XRPLModelException):
            SetFee(
                reserve_base=int(reserve_base_drops),  # Pre-XRPFees amendment
                reserve_base_drops=reserve_base_drops,  # Post-XRPFees amendment
                reserve_increment_drops=reserve_increment_drops,
                base_fee_drops=base_fee,
            )
        with self.assertRaises(XRPLModelException):
            Transaction.from_xrpl(set_fee_dict)

    def test_from_xrpl_unl_modify(self):
        ledger_sequence = 1600000
        validator = "ED6629D456285AE3613B285F65BBFF168D695BA3921F309949AFCD2CA7AFEC16FE"
        unl_modify_dict = {
            "Account": "rrrrrrrrrrrrrrrrrrrrrhoLvTp",
            "Fee": "0",
            "LedgerSequence": ledger_sequence,
            "Sequence": 0,
            "SigningPubKey": "",
            "TransactionType": "UNLModify",
            "UNLModifyDisabling": 1,
            "UNLModifyValidator": validator,
        }
        expected = UNLModify(
            ledger_sequence=ledger_sequence,
            unl_modify_disabling=1,
            unl_modify_validator=validator,
        )
        actual = PseudoTransaction.from_xrpl(unl_modify_dict)
        self.assertEqual(actual, expected)
        full_dict = {**unl_modify_dict, "Flags": 0, "TxnSignature": ""}
        self.assertEqual(actual.to_xrpl(), full_dict)
