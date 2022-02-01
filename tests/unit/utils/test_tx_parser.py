from unittest import TestCase

import xrpl.utils

transaction = {
    "Account": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
    "Amount": {
        "currency": "43656C65627269747950756E6B73000000000000",
        "issuer": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
        "value": "200",
    },
    "Destination": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
    "Fee": "10",
    "Flags": 2147483648,
    "LastLedgerSequence": 69301905,
    "Sequence": 69262332,
    "SigningPubKey": """
ED5375298D273C03DB38AF4BB77A883B44790A7209B129F3E52D16B9CD7ADF5ACF
    """,
    "TransactionType": "Payment",
    "TxnSignature": """
0B65FCB22323D3BF4532E046481A7F545FF49634AF5B6DD8A8CD3199A16297C5660C8A6B5E845E3F2EDA2E86A5D7BDD4301D7CF5C16CA55D13043F5D4DCCC30F
    """,
    "date": 696642440,
    "hash": "38276A4E194FB8A7CAE0AE8A849048116F66366935B22785A33207EE08D80D78",
    "inLedger": 69301903,
    "ledger_index": 69301903,
    "meta": {
        "AffectedNodes": [
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-200",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
                            "value": "10000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                            "value": "0",
                        },
                        "LowNode": "14e",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
11D048146AA277225904FCF8FF5D62FAB6B17FD9082392688A5B5FB4934D7874
                    """,
                    "PreviousFields": {
                        "Balance": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "0",
                        },
                    },
                    "PreviousTxnID": """
D03316D6DD24E755978D26459BF5523A050B33A8ACC44CC2EE816E97AD55EA91
                    """,
                    "PreviousTxnLgrSeq": 69227871,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-2861150",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                            "value": "10000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                            "value": "0",
                        },
                        "LowNode": "42a",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
8ADF6DAAC69842BE2B2015764B25B7F33C091D6D2AF0006F8C686C81AFA082AE
                    """,
                    "PreviousFields": {
                        "Balance": {
                            "currency": "43656C65627269747950756E6B73000000000000",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-2861350",
                        },
                    },
                    "PreviousTxnID": """
A1BC7C0D089E28F841F3414DB8D732EA41D4C88000370C466801DF4B75715B58
                    """,
                    "PreviousTxnLgrSeq": 69301903,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                        "Balance": "35891433",
                        "Flags": 0,
                        "OwnerCount": 2,
                        "Sequence": 69262333,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
EB15B3164948318C04A2E92D465E9EBA0870F3D3ACA990C4CCF57D22F9CA30C9
                    """,
                    "PreviousFields": {
                        "Balance": "35891443",
                        "Sequence": 69262332,
                    },
                    "PreviousTxnID": """
A1BC7C0D089E28F841F3414DB8D732EA41D4C88000370C466801DF4B75715B58
                    """,
                    "PreviousTxnLgrSeq": 69301903,
                },
            },
        ],
        "TransactionIndex": 3,
        "TransactionResult": "tesSUCCESS",
        "delivered_amount": {
            "currency": "43656C65627269747950756E6B73000000000000",
            "issuer": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
            "value": "200",
        },
    },
    "validated": True,
}


class TestTxParser(TestCase):
    def test_valid_metadata_missing_account(self):
        meta = transaction.copy().pop("Account")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.parse_balance_changes(metadata=meta)

    def test_valid_metadata_missing_meta(self):
        meta = transaction.copy().pop("meta")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.parse_balance_changes(metadata=meta)

    def test_valid_metadata_missing_nodes(self):
        meta = transaction.copy()["meta"].pop("AffectedNodes")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.parse_balance_changes(metadata=meta)

    def test_parse_balace_changes(self):
        actual = xrpl.utils.parse_balance_changes(metadata=transaction)
        expected = {
            "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8": [
                {
                    "Counterparty": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-200.0",
                },
                {
                    "Counterparty": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200.0",
                },
            ],
            "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200.0",
                },
            ],
            "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200.0",
                },
                {
                    "Counterparty": "",
                    "Currency": "XRP",
                    "Value": "-0.000010",
                },
            ],
        }
        self.assertEqual(actual, expected)

    def test_parse_final_balances(self):
        actual = xrpl.utils.parse_final_balances(metadata=transaction)
        expected = {
            "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8": [
                {
                    "Counterparty": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-200.0",
                },
                {
                    "Counterparty": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-2861150.0",
                },
            ],
            "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200.0",
                },
            ],
            "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "2861150.0",
                },
                {
                    "Counterparty": "",
                    "Currency": "XRP",
                    "Value": "35.891433",
                },
            ],
        }
        self.assertEqual(actual, expected)
