import copy
from unittest import TestCase

import xrpl.utils

TEST_TXN = {
    "engine_result": "tesSUCCESS",
    "engine_result_code": 0,
    "engine_result_message": "The transaction was applied. Only final in a validated "
    "ledger.",
    "ledger_hash": "D22FF847C0CD3B83BBAC08DA456207C1682E91B8E31C024F1341546F1727E96F",
    "ledger_index": 70948801,
    "meta": {
        "AffectedNodes": [
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "610.0963958078583",
                        },
                        "Flags": 1114112,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "HighNode": "1c19",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                            "value": "1000000000",
                        },
                        "LowNode": "0",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": "0B0388546E94E2B339A52C70CE9B7791FDF104F114C94CEACB2"
                    "A9440819DD435",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "610.800602986901",
                        },
                    },
                    "PreviousTxnID": "87B4598500ABEA310502C714DDEA2A8DD7A2E0858D9C104F6"
                    "AEFD99C8DB121C1",
                    "PreviousTxnLgrSeq": 70948688,
                }
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-0.7688823004351198",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                            "value": "1000000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "LowNode": "1fce",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": "14BE4365C33BE6BF6AF293C0CF48F8556037541C016DDF37A8A"
                    "C71C028803206",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-0.0660807245441266",
                        },
                    },
                    "PreviousTxnID": "2F5829A2F449EBEF449B86461EF3348C9A3050199FCB1DD04"
                    "AE09744AB298276",
                    "PreviousTxnLgrSeq": 70608646,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                        "Balance": "84341395",
                        "Flags": 0,
                        "OwnerCount": 16,
                        "Sequence": 67702088,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": "3CCC83874FDC50BA6F111748515A3EECEEE13977F5AFBE72308"
                    "C90D6129E8BD8",
                    "PreviousFields": {
                        "Balance": "85341410",
                        "Sequence": 67702087,
                    },
                    "PreviousTxnID": "2F5829A2F449EBEF449B86461EF3348C9A3050199FCB1DD04"
                    "AE09744AB298276",
                    "PreviousTxnLgrSeq": 70608646,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                        "Balance": "230786754961",
                        "Flags": 0,
                        "MessageKey": "02000000000000000000000000C40291E3D8888D158B3370"
                        "626B71BDF2C883E942",
                        "OwnerCount": 9,
                        "Sequence": 59186941,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": "73F7B01109BB599FEDF75529CD8A6521890745E813DD45EC36A"
                    "73828EDDD56BF",
                    "PreviousFields": {"Balance": "230785754961"},
                    "PreviousTxnID": "5A554D3D6FCFFA92E35991937D6A3F3CC228FB84C4E464EBB"
                    "6AF2816AEBD4409",
                    "PreviousTxnLgrSeq": 70948695,
                }
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                        "BookDirectory": "F0B9A528CE25FE77C51C38040A7FEC016C2C841E74C14"
                        "18D5B050E194D5C38E3",
                        "BookNode": "0",
                        "Flags": 0,
                        "OwnerNode": "0",
                        "Sequence": 59186940,
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "90.91728842410901",
                        },
                        "TakerPays": "129364093",
                    },
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": "7C36CEDFC5D76532990242382A94943F2B3A0C54C80A2623938"
                    "8ED2DC07E1CD1",
                    "PreviousFields": {
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "91.62009",
                        },
                        "TakerPays": "130364093",
                    },
                    "PreviousTxnID": "5A554D3D6FCFFA92E35991937D6A3F3CC228FB84C4E464EBB"
                    "6AF2816AEBD4409",
                    "PreviousTxnLgrSeq": 70948695,
                }
            },
        ],
        "TransactionIndex": 18,
        "TransactionResult": "tesSUCCESS",
    },
    "status": "closed",
    "transaction": {
        "Account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
        "Fee": "15",
        "Flags": 2148139008,
        "LastLedgerSequence": 70948809,
        "Sequence": 67702087,
        "SigningPubKey": "EDD923A96C6FCFCC40E90F3C8838205C82FF0317FF2FF1196A4D196E6B960"
        "F5371",
        "TakerGets": "1000000",
        "TakerPays": {
            "currency": "USD",
            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
            "value": "0.68233163",
        },
        "TransactionType": "OfferCreate",
        "TxnSignature": "92E5861C3DBD930343B1C5F99CF543B846E87AA08A9236D482E08F184B035B"
        "D2521C3C0B32A72B88B463329F809262C9FF3D4C2F2C5D00A2E6B4F8E56F4DE60E",
        "date": 703116450,
        "hash": "2EEC0D1D67C95FDF5B3ADFAAA45164C682A694D5BE4164DD182CB3A2D16E4E32",
        "owner_funds": "42341395",
    },
    "type": "transaction",
    "validated": True,
}

NO_OFFERS_TXN = {
    "Account": "rGDreBvnHrX1get7na3J4oowN19ny4GzFn",
    "Amount": "211872914",
    "Destination": "rLQUo6VbTMHA7dFTpCTzSzTKAUuWSy7u3K",
    "DestinationTag": 3611374809,
    "Fee": "10460",
    "Flags": 2147483648,
    "LastLedgerSequence": 69458005,
    "Sequence": 80949,
    "SigningPubKey": "02024F808D657322E73CEA9A0109CDBD9A3A56552CA87F847DD8558B47CD0F2E"
    "20",
    "TransactionType": "Payment",
    "TxnSignature": "30440220324FF9E7E4A9D1DE162FBB3E8B57BF02C65BA9C0ED070F48B462C8665"
    "F3CD40402206AFEF4838FD3207F6FEF06ACF63A04C80E64598B0C5C51456D3DCFC458D0CA34",
    "date": 697255801,
    "hash": "AE24F3D18B0D2EA407E7F50926AAFB5DCE21B1AFC35D796B7FEFC4FA56D8E5E7",
    "inLedger": 69457007,
    "ledger_index": 69457007,
    "meta": {
        "AffectedNodes": [
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rGDreBvnHrX1get7na3J4oowN19ny4GzFn",
                        "Balance": "2743441448059",
                        "Flags": 0,
                        "OwnerCount": 0,
                        "Sequence": 80950,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": "8719BD164C9F79A760E19FB64691885E63CC595032E559971F8"
                    "9C1E22EAEC220",
                    "PreviousFields": {
                        "Balance": "2743653331433",
                        "Sequence": 80949,
                    },
                    "PreviousTxnID": "8DD9649A8E789257A61CD7223A507602CED9F08BCF1FFC9F2"
                    "E79C08DCC2863E8",
                    "PreviousTxnLgrSeq": 69457007,
                }
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rLQUo6VbTMHA7dFTpCTzSzTKAUuWSy7u3K",
                        "Balance": "815244743639",
                        "Flags": 131072,
                        "OwnerCount": 0,
                        "Sequence": 14175,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": "969F1B7A63CC54C344B2990659AFD3F8BB541D03B574B48EED4"
                    "1A32DA51AA53A",
                    "PreviousFields": {"Balance": "815032870725"},
                    "PreviousTxnID": "150DB308EEC5BBB4037E8953D3D5B42371D49033012D16DC1"
                    "170036DD76D2AD2",
                    "PreviousTxnLgrSeq": 69456777,
                },
            },
        ],
        "TransactionIndex": 7,
        "TransactionResult": "tesSUCCESS",
        "delivered_amount": "211872914",
    },
    "validated": True,
}


class TestBalanceChanges(TestCase):
    def test_valid_metadata_missing_account(self):
        bc_test_no_account = copy.deepcopy(TEST_TXN)
        bc_test_no_account["transaction"].pop("Account")
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_balance_changes(transaction=bc_test_no_account)

    def test_valid_metadata_missing_meta(self):
        bc_test_no_meta = copy.deepcopy(TEST_TXN)
        bc_test_no_meta.pop("meta")
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_balance_changes(transaction=bc_test_no_meta)

    def test_valid_metadata_missing_nodes(self):
        bc_test_no_nodes = copy.deepcopy(TEST_TXN)
        bc_test_no_nodes["meta"].pop("AffectedNodes")
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_balance_changes(transaction=bc_test_no_nodes)

    def test_parse_balace_changes(self):
        actual = xrpl.utils.parse_balance_changes(transaction=TEST_TXN)
        expected = {
            "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe": [
                {
                    "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                    "currency": "USD",
                    "value": "-0.7042071790427",
                },
                {"counterparty": "", "currency": "XRP", "value": "1.000000"},
            ],
            "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq": [
                {
                    "counterparty": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                    "currency": "USD",
                    "value": "0.7042071790427",
                },
                {
                    "counterparty": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                    "currency": "USD",
                    "value": "-0.7028015758909932",
                },
            ],
            "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A": [
                {
                    "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                    "currency": "USD",
                    "value": "0.7028015758909932",
                },
                {"counterparty": "", "currency": "XRP", "value": "-1.000015"},
            ],
        }
        self.assertEqual(actual, expected)

    def test_parse_final_balances(self):
        actual = xrpl.utils.parse_final_balances(transaction=TEST_TXN)
        expected = {
            "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe": [
                {
                    "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                    "currency": "USD",
                    "value": "610.0963958078583",
                },
                {"counterparty": "", "currency": "XRP", "value": "230786.754961"},
            ],
            "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq": [
                {
                    "counterparty": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                    "currency": "USD",
                    "value": "-610.0963958078583",
                },
                {
                    "counterparty": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                    "currency": "USD",
                    "value": "-0.7688823004351198",
                },
            ],
            "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A": [
                {
                    "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                    "currency": "USD",
                    "value": "0.7688823004351198",
                },
                {"counterparty": "", "currency": "XRP", "value": "84.341395"},
            ],
        }
        self.assertEqual(actual, expected)

    def test_parse_previous_balances(self):
        actual = xrpl.utils.parse_previous_balances(transaction=TEST_TXN)
        expected = {
            "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe": [
                {
                    "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                    "currency": "USD",
                    "value": "610.8006029869010",
                },
                {"counterparty": "", "currency": "XRP", "value": "230785.754961"},
            ],
            "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq": [
                {
                    "counterparty": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                    "currency": "USD",
                    "value": "-610.8006029869010",
                },
                {
                    "counterparty": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                    "currency": "USD",
                    "value": "-0.0660807245441266",
                },
            ],
            "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A": [
                {
                    "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                    "currency": "USD",
                    "value": "0.0660807245441266",
                },
                {"counterparty": "", "currency": "XRP", "value": "85.341410"},
            ],
        }
        self.assertEqual(actual, expected)


class TestOrderbookChanges(TestCase):
    def test_valid_metadata_missing_account(self):
        oc_test_no_account = copy.deepcopy(TEST_TXN)
        oc_test_no_account["transaction"].pop("Account")
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_order_book_changes(transaction=oc_test_no_account)

    def test_valid_metadata_missing_meta(self):
        oc_test_no_meta = copy.deepcopy(TEST_TXN)
        oc_test_no_meta.pop("meta")
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_order_book_changes(transaction=oc_test_no_meta)

    def test_valid_metadata_missing_nodes(self):
        oc_test_no_nodes = copy.deepcopy(TEST_TXN)
        oc_test_no_nodes["meta"].pop("AffectedNodes")
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_order_book_changes(transaction=oc_test_no_nodes)

    def test_no_offers_affected(self):
        actual = xrpl.utils.parse_order_book_changes(transaction=NO_OFFERS_TXN)
        expected = {}

        self.assertEqual(actual, expected)

    def test_parse_orderbook_changes(self):
        actual = xrpl.utils.parse_order_book_changes(transaction=TEST_TXN)
        expected = {
            "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe": [
                {
                    "taker_pays": {
                        "final_amount": {
                            "issuer": "",
                            "currency": "XRP",
                            "value": "129.364093",
                        },
                        "previous_value": "130.364093",
                    },
                    "taker_gets": {
                        "final_amount": {
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "90.91728842410901",
                        },
                        "previous_value": "91.62009",
                    },
                    "sell": False,
                    "sequence": 59186940,
                    "status": "partially-filled",
                    "quality": "1.422876718414050841478774945",
                    "direction": "buy",
                    "total_received": {
                        "final_amount": {
                            "issuer": "",
                            "currency": "XRP",
                            "value": "129.364093",
                        },
                        "previous_value": "130.364093",
                    },
                    "total_paid": {
                        "final_amount": {
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "90.91728842410901",
                        },
                        "previous_value": "91.62009",
                    },
                    "account": "rpXhhWmCvDwkzNtRbm7mmD1vZqdfatQNEe",
                }
            ]
        }
        self.assertEqual(actual, expected)
