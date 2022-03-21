from unittest import TestCase

import xrpl.utils

balance_changes_tx = {
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


class TestBalanceChanges(TestCase):
    def test_valid_metadata_missing_account(self):
        meta = balance_changes_tx.copy().pop("Account")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseBalanceChanges(metadata=meta)

    def test_valid_metadata_missing_meta(self):
        meta = balance_changes_tx.copy().pop("meta")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseBalanceChanges(metadata=meta)

    def test_valid_metadata_missing_nodes(self):
        meta = balance_changes_tx.copy()["meta"].pop("AffectedNodes")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseBalanceChanges(metadata=meta)

    def test_parse_balace_changes(self):
        actual = xrpl.utils.ParseBalanceChanges(
            metadata=balance_changes_tx
        ).all_balances
        expected = {
            "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8": [
                {
                    "Counterparty": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-200",
                },
                {
                    "Counterparty": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200",
                },
            ],
            "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200",
                },
            ],
            "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-200",
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
        actual = xrpl.utils.ParseFinalBalances(metadata=balance_changes_tx).all_balances
        expected = {
            "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8": [
                {
                    "Counterparty": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-200",
                },
                {
                    "Counterparty": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-2861150",
                },
            ],
            "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "200",
                },
            ],
            "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "2861150",
                },
                {
                    "Counterparty": "",
                    "Currency": "XRP",
                    "Value": "35.891433",
                },
            ],
        }
        self.assertEqual(actual, expected)

    def test_parse_previous_balances(self):
        actual = xrpl.utils.ParsePreviousBalances(
            metadata=balance_changes_tx
        ).all_balances
        expected = {
            "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8": [
                {
                    "Counterparty": "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "0",
                },
                {
                    "Counterparty": "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "-2861350",
                },
            ],
            "r396SL8QQR3hCt4vhEJL2dpWwVdE1ysh9y": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "0",
                },
            ],
            "rMXmHfF2yugfVtYPkc3gVqtyAqSq6HYmBp": [
                {
                    "Counterparty": "rsfZH5bmvAUk334hKRJMzoFEVkeFvWCdC8",
                    "Currency": "43656C65627269747950756E6B73000000000000",
                    "Value": "2861350",
                },
                {
                    "Counterparty": "",
                    "Currency": "XRP",
                    "Value": "35.891443",
                },
            ],
        }
        self.assertEqual(actual, expected)


orderbook_changes_tx_subscribtion = {
    "engine_result": "tesSUCCESS",
    "engine_result_code": 0,
    "engine_result_message": """
The transaction was applied. Only final in a validated ledger.
""",
    "ledger_hash": "6847B4C9D78D46FE2E29DB10A29A047F7EEDC398EA973FBC4EFDD0FD8075A2F6",
    "ledger_index": 69452036,
    "meta": {
        "AffectedNodes": [
            {
                "CreatedNode": {
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
44D1365DA45F13006343BE0015038D590E08F10AA0DF5C2CBFA225A37644531D
""",
                    "NewFields": {
                        "Account": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                        "BookDirectory": """
79C54A4EBD69AB2EADCE313042F36092BE432423CC6A4F784E16B11A4E4DA38E
""",
                        "Expiration": 703236173,
                        "Sequence": 32522122,
                        "TakerGets": "3359492729",
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "2145.767142696333",
                        },
                    },
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "ExchangeRate": "4e16b11a4e4da38b",
                        "Flags": 0,
                        "RootIndex": """
79C54A4EBD69AB2EADCE313042F36092BE432423CC6A4F784E16B11A4E4DA38B
""",
                        "TakerGetsCurrency": "0000000000000000000000000000000000000000",
                        "TakerGetsIssuer": "0000000000000000000000000000000000000000",
                        "TakerPaysCurrency": "0000000000000000000000005553440000000000",
                        "TakerPaysIssuer": "2ADB0B3959D60A6E6991F729E1918B7163925230",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
79C54A4EBD69AB2EADCE313042F36092BE432423CC6A4F784E16B11A4E4DA38B
""",
                },
            },
            {
                "CreatedNode": {
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
79C54A4EBD69AB2EADCE313042F36092BE432423CC6A4F784E16B11A4E4DA38E
""",
                    "NewFields": {
                        "ExchangeRate": "4e16b11a4e4da38e",
                        "RootIndex": """
79C54A4EBD69AB2EADCE313042F36092BE432423CC6A4F784E16B11A4E4DA38E
""",
                        "TakerPaysCurrency": "0000000000000000000000005553440000000000",
                        "TakerPaysIssuer": "2ADB0B3959D60A6E6991F729E1918B7163925230",
                    },
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                        "Balance": "41100393086",
                        "Flags": 0,
                        "OwnerCount": 11,
                        "Sequence": 32522123,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
7B27505E5F915E531ED38221CCD639DD939AE29CDAC5C58436B4030D1D66D5DD
""",
                    "PreviousFields": {
                        "Balance": "41100393103",
                        "Sequence": 32522122,
                    },
                    "PreviousTxnID": """
74A20241A186D394D23B4843ECDF74EB22F581DB511FCF329D81DD1E9C13431B
""",
                    "PreviousTxnLgrSeq": 69452031,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Flags": 0,
                        "Owner": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                        "RootIndex": """
D9AC75B265FBABD909B43FD8B254796F805585FD587C9112E301A5E582FA87A7
""",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
D9AC75B265FBABD909B43FD8B254796F805585FD587C9112E301A5E582FA87A7
""",
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "Account": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                        "BookDirectory": """
79C54A4EBD69AB2EADCE313042F36092BE432423CC6A4F784E16B11A4E4DA38B
""",
                        "BookNode": "0",
                        "Expiration": 703236153,
                        "Flags": 0,
                        "OwnerNode": "0",
                        "PreviousTxnID": """
74A20241A186D394D23B4843ECDF74EB22F581DB511FCF329D81DD1E9C13431B
""",
                        "PreviousTxnLgrSeq": 69452031,
                        "Sequence": 32522121,
                        "TakerGets": "1874486084",
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "1197.267258169058",
                        },
                    },
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
F9A051615D4FAA6B8F00BDCD1376D94F83BAAD9364139855BD66433BF17C9D19
""",
                },
            },
        ],
        "TransactionIndex": 39,
        "TransactionResult": "tesSUCCESS",
    },
    "status": "closed",
    "transaction": {
        "Account": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
        "Expiration": 703236173,
        "Fee": "17",
        "Flags": 2147483648,
        "LastLedgerSequence": 69452037,
        "OfferSequence": 32522121,
        "Sequence": 32522122,
        "SigningPubKey": """
03E87A456AC78712EA2954EA074071620B9168D0DB5FB72888078BDF1E1C0EC50A
""",
        "TakerGets": "3359492729",
        "TakerPays": {
            "currency": "USD",
            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
            "value": "2145.767142696333",
        },
        "TransactionType": "OfferCreate",
        "TxnSignature": """
3045022100AABDFA728E35638D22E30F3CB533FABB88DF6A6CF3E70E5D1CCBB9D23F86315702203D6E08FDF1CBC6FFB7905EC8D9650DC70C1737C2A697A3530CA86D3D665259FF
""",
        "date": 697236180,
        "hash": "A3ABB33950808C0F93D61E6C64A005D067FD6E1AC3D855959D95A41997209F32",
        "owner_funds": "41068393086",
    },
    "type": "transaction",
    "validated": True,
}

orderbook_changes_tx = {
    "Account": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
    "Fee": "1200",
    "Flags": 2147614720,
    "LastLedgerSequence": 69169320,
    "Sequence": 31391456,
    "SigningPubKey": """
03E87A456AC78712EA2954EA074071620B9168D0DB5FB72888078BDF1E1C0EC50A
""",
    "TakerGets": {
        "currency": "USD",
        "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
        "value": "1671.827223544551",
    },
    "TakerPays": {
        "currency": "USD",
        "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
        "value": "1675.31194274857",
    },
    "TransactionType": "OfferCreate",
    "TxnSignature": """
3044022079ECA99C7235B8528966C89A949E45F2E7609FE90B0192C78D667E7F2985ED2B0220243DE63EC8B7E5A2D957D70B345A1644E69A8627C77346D77D286FD633CB9BA9
""",
    "date": 696117740,
    "hash": "31D4DC7FEF855B38A7A1536592B988FF21FE4128C92B76CD0501006B0DA93DBC",
    "inLedger": 69169318,
    "ledger_index": 69169318,
    "meta": {
        "AffectedNodes": [
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Flags": 0,
                        "IndexPrevious": "4",
                        "Owner": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                        "RootIndex": """
E5EDA666FF7FA049136BE952984ABDE9F59BD97C0EEFD1ADB93094E27047573A
""",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
091BE53F6AFE8089FCD573C96D0E3B7E9145FEA4057924EA298D950F7F667352""",
                }
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-4.5134501735959",
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
                    "LedgerIndex": """
14BE4365C33BE6BF6AF293C0CF48F8556037541C016DDF37A8AC71C028803206
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-205.9154501735959",
                        },
                    },
                    "PreviousTxnID": """
FED338B208D5D50FCCCF3CA5CEC5D032F512D0A3CA56F1882B0A457245B6B68E
""",
                    "PreviousTxnLgrSeq": 69161184,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-246.3502409272913",
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
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "0",
                        },
                        "LowNode": "991",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
1B0CE75F44E3498B444ACB80AA40E3212954BBD55D237205182612EA8998877F
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-46.35024092729137",
                        },
                    },
                    "PreviousTxnID": """
0EC4B0DA2998553D2F6E97FF8D71C26AC33F46EDC82C7785D53E25EBD1180DFC
""",
                    "PreviousTxnLgrSeq": 69162068,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-31668.15001252759",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                            "value": "1000000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "LowNode": "29d",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
3924BC09BEECCE4B411D17789803B66074F248365D70A9757A21478352D75383
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-32693.92830690189",
                        },
                    },
                    "PreviousTxnID": """
118C94774DBFE3643ABA8D785FAAAB4610D11F7D2DD1B665E46B20449163BB88
""",
                    "PreviousTxnLgrSeq": 69169298,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                        "Balance": "60770325",
                        "Flags": 0,
                        "OwnerCount": 8,
                        "Sequence": 67701667,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
3CCC83874FDC50BA6F111748515A3EECEEE13977F5AFBE72308C90D6129E8BD8
""",
                    "PreviousFields": {
                        "OwnerCount": 9,
                    },
                    "PreviousTxnID": """
0EC4B0DA2998553D2F6E97FF8D71C26AC33F46EDC82C7785D53E25EBD1180DFC
""",
                    "PreviousTxnLgrSeq": 69162068,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-381.1004148956297",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rUqK2eC8TMdm64bJqXMsUcavEbVuWy5Myv",
                            "value": "1000000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "0",
                        },
                        "LowNode": "9b9",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
4ABA943D2BA731CAB87DB69D8634B0CF63AA49EFE80A8D0EB3536527640B2392
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "0",
                        },
                    },
                    "PreviousTxnID": """
080A666F7B44B96A396C451B64EB2781CBB8C2867A764B07D66A920CC131D030
""",
                    "PreviousTxnLgrSeq": 69161415,
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "Account": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                        "BookDirectory": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A54235978E783E000
""",
                        "BookNode": "0",
                        "Flags": 131072,
                        "OwnerNode": "5",
                        "PreviousTxnID": """
118C94774DBFE3643ABA8D785FAAAB4610D11F7D2DD1B665E46B20449163BB88
""",
                        "PreviousTxnLgrSeq": 69169298,
                        "Sequence": 5811,
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "0",
                        },
                    },
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
4BE6405FE15E19B4F93A293F58290F144FAEB629EC1028133C00E8D0CCDB6114
""",
                    "PreviousFields": {
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "1023.730832708886",
                        },
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "1018.612178545341",
                        },
                    },
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "Account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                        "BookDirectory": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A542359B2D28A8C19
""",
                        "BookNode": "0",
                        "Flags": 131072,
                        "OwnerNode": "0",
                        "PreviousTxnID": """
A7F8097BAC5633467CCB7EFAE28ABCF113FF415A60D49619232B31A2B32B5EEA
""",
                        "PreviousTxnLgrSeq": 69161355,
                        "Sequence": 67701665,
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "0",
                        },
                    },
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
7411B28D5B3E26571A1D91AC89C73B3FDE288CB46065489D69B788856BD44F09""",
                    "PreviousFields": {
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "201",
                        },
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "200",
                        },
                    },
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Flags": 0,
                        "IndexPrevious": "9c1",
                        "Owner": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                        "RootIndex": """
7E1247F78EFC74FA9C0AE39F37AF433966615EB9B757D8397C068C2849A8F4A5""",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
7AD460495D336CE5241872544EA21EF0EFCEF0AD839EAA8BA00682848B6CAFA5
""",
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                        "Balance": "37408409876",
                        "Flags": 0,
                        "OwnerCount": 13,
                        "Sequence": 31391457,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
7B27505E5F915E531ED38221CCD639DD939AE29CDAC5C58436B4030D1D66D5DD
""",
                    "PreviousFields": {
                        "Balance": "37408411076",
                        "OwnerCount": 14,
                        "Sequence": 31391456,
                    },
                    "PreviousTxnID": """
951C4B70F05990C955085CD88618F92AE5E4EE94AADC5B0F8B6B164C4E993B8C
""",
                    "PreviousTxnLgrSeq": 69169318,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-8286.99876471854",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                            "value": "1000000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "0",
                        },
                        "LowNode": "4af",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
9723C56F7296CD00954B197C97C2EEE149CA42542F025F067A0037B0D4734CE8
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-7268.386586173199",
                        },
                    },
                    "PreviousTxnID": """
118C94774DBFE3643ABA8D785FAAAB4610D11F7D2DD1B665E46B20449163BB88
""",
                    "PreviousTxnLgrSeq": 69169298,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Flags": 0,
                        "Owner": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                        "RootIndex": """
99122F08CB195CCB745D5223934ECB1E667A56EFCABB76D3F88EEB229A49ED62
""",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
99122F08CB195CCB745D5223934ECB1E667A56EFCABB76D3F88EEB229A49ED62
""",
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "1606.637293348074",
                        },
                        "Flags": 1114112,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "HighNode": "2052",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                            "value": "0",
                        },
                        "LowNode": "0",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
AF2AE23E8D43CE1762DB2D48A321DD1A8E39AFA3B88CCCA8F4A8EA74DAD0CB2F
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "0.004050682650461922",
                        },
                    },
                    "PreviousTxnID": """
DF12A8C419F7568156AC1A2835D047A2700CA7937DA270765937AC063D38FB99
""",
                    "PreviousTxnLgrSeq": 69169042,
                },
            },
            {
                "ModifiedNode": {
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
B7D526FDDF9E3B3F95C3DC97C353065B0482302500BBB8051A5C090B596C6133
""",
                    "PreviousTxnID": """
951C4B70F05990C955085CD88618F92AE5E4EE94AADC5B0F8B6B164C4E993B8C
""",
                    "PreviousTxnLgrSeq": 69169318,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Flags": 0,
                        "IndexNext": "0",
                        "IndexPrevious": "0",
                        "Owner": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                        "RootIndex": """
D9AC75B265FBABD909B43FD8B254796F805585FD587C9112E301A5E582FA87A7
""",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
D9AC75B265FBABD909B43FD8B254796F805585FD587C9112E301A5E582FA87A7
""",
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rUqK2eC8TMdm64bJqXMsUcavEbVuWy5Myv",
                        "BookDirectory": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A542373D8FE36B000
""",
                        "BookNode": "0",
                        "Flags": 131072,
                        "OwnerNode": "0",
                        "Sequence": 69051546,
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "62.8919636313763",
                        },
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "62.7598905077505",
                        },
                    },
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
E0C7E0C5FA2F3FF18DDFD3C9DEB87D7B066E4A3B022ED7985A97A2585B052FA1
""",
                    "PreviousFields": {
                        "TakerGets": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "444.7943735879148",
                        },
                        "TakerPays": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "443.8603054033802",
                        },
                    },
                    "PreviousTxnID": """
4C09BBABA57B8A7DDC2910AF73EEB7488633485FFE5A67C15A41904C0F5CC890
""",
                    "PreviousTxnLgrSeq": 69163916,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                        "Balance": "24135365991",
                        "Flags": 0,
                        "MessageKey": """
02000000000000000000000000C03555B48C4398613CE55C8B728FFF2C91265101
""",
                        "OwnerCount": 35,
                        "Sequence": 5813,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
E3795FE99A17BDE69DC0234FF295C811302E451B773A8D96EAAF3846628E8A43
""",
                    "PreviousFields": {
                        "OwnerCount": 36,
                    },
                    "PreviousTxnID": """
FAC486BF19599BE8D18A3D9A8E386CB0C9E344AE6A3527704E7C76DD09546BA3
""",
                    "PreviousTxnLgrSeq": 69168458,
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-62.1281588114633",
                        },
                        "Flags": 2228224,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rUqK2eC8TMdm64bJqXMsUcavEbVuWy5Myv",
                            "value": "1000000000",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "value": "0",
                        },
                        "LowNode": "2049",
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
E76AAC93130B9416FC6DFA79B2135BAE5D4D6D9D15B449EE3809AFA5ED2A8544
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-444.7943735879148",
                        },
                    },
                    "PreviousTxnID": """
080A666F7B44B96A396C451B64EB2781CBB8C2867A764B07D66A920CC131D030""",
                    "PreviousTxnLgrSeq": 69161415,
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "ExchangeRate": "54235978e783e000",
                        "Flags": 0,
                        "RootIndex": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A54235978E783E000
""",
                        "TakerGetsCurrency": "0000000000000000000000005553440000000000",
                        "TakerGetsIssuer": "2ADB0B3959D60A6E6991F729E1918B7163925230",
                        "TakerPaysCurrency": "0000000000000000000000005553440000000000",
                        "TakerPaysIssuer": "0A20B3C85F482532A9578DBB3950B85CA06594D1",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A54235978E783E000
""",
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "ExchangeRate": "542359b2d28a8c19",
                        "Flags": 0,
                        "RootIndex": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A542359B2D28A8C19""",
                        "TakerGetsCurrency": "0000000000000000000000005553440000000000",
                        "TakerGetsIssuer": "2ADB0B3959D60A6E6991F729E1918B7163925230",
                        "TakerPaysCurrency": "0000000000000000000000005553440000000000",
                        "TakerPaysIssuer": "0A20B3C85F482532A9578DBB3950B85CA06594D1",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
E8900917D0B37ED23351E4A7276E10B5BE987CCD4EA2A08A542359B2D28A8C19
""",
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "0",
                        },
                        "Flags": 2097152,
                        "HighLimit": {
                            "currency": "USD",
                            "issuer": "rs9tBKt96q9gwrePKPqimUuF7vErgMaker",
                            "value": "0",
                        },
                        "HighNode": "0",
                        "LowLimit": {
                            "currency": "USD",
                            "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "value": "0",
                        },
                        "LowNode": "9c2",
                        "PreviousTxnID": """
951C4B70F05990C955085CD88618F92AE5E4EE94AADC5B0F8B6B164C4E993B8C
""",
                        "PreviousTxnLgrSeq": 69169318,
                    },
                    "LedgerEntryType": "RippleState",
                    "LedgerIndex": """
FF9E43FA751AC8E4E24D3CCF84ED7C41207E335F0C53BA2CFF852A238ED545EC
""",
                    "PreviousFields": {
                        "Balance": {
                            "currency": "USD",
                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                            "value": "-1602.912018627853",
                        },
                        "Flags": 2228224,
                    },
                },
            },
        ],
        "TransactionIndex": 86,
        "TransactionResult": "tesSUCCESS",
    },
    "validated": True,
}

orderbook_changes_tx_no_offers = {
    "Account": "rGDreBvnHrX1get7na3J4oowN19ny4GzFn",
    "Amount": "211872914",
    "Destination": "rLQUo6VbTMHA7dFTpCTzSzTKAUuWSy7u3K",
    "DestinationTag": 3611374809,
    "Fee": "10460",
    "Flags": 2147483648,
    "LastLedgerSequence": 69458005,
    "Sequence": 80949,
    "SigningPubKey": """
02024F808D657322E73CEA9A0109CDBD9A3A56552CA87F847DD8558B47CD0F2E20
""",
    "TransactionType": "Payment",
    "TxnSignature": """
30440220324FF9E7E4A9D1DE162FBB3E8B57BF02C65BA9C0ED070F48B462C8665F3CD40402206AFEF4838FD3207F6FEF06ACF63A04C80E64598B0C5C51456D3DCFC458D0CA34
""",
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
                    "LedgerIndex": """
8719BD164C9F79A760E19FB64691885E63CC595032E559971F89C1E22EAEC220
""",
                    "PreviousFields": {
                        "Balance": "2743653331433",
                        "Sequence": 80949,
                    },
                    "PreviousTxnID": """
8DD9649A8E789257A61CD7223A507602CED9F08BCF1FFC9F2E79C08DCC2863E8
""",
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
                    "LedgerIndex": """
969F1B7A63CC54C344B2990659AFD3F8BB541D03B574B48EED41A32DA51AA53A
""",
                    "PreviousFields": {"Balance": "815032870725"},
                    "PreviousTxnID": """
150DB308EEC5BBB4037E8953D3D5B42371D49033012D16DC1170036DD76D2AD2
""",
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


class TestOrderbookChanges(TestCase):
    def test_valid_metadata_missing_account_subscribtion(self):
        meta = orderbook_changes_tx_subscribtion.copy()["transaction"].pop("Account")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseOrderBookChanges(metadata=meta)

    def test_valid_metadata_missing_account(self):
        meta = orderbook_changes_tx.copy().pop("Account")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseOrderBookChanges(metadata=meta)

    def test_valid_metadata_missing_meta(self):
        meta = orderbook_changes_tx.copy().pop("meta")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseOrderBookChanges(metadata=meta)

    def test_valid_metadata_missing_nodes(self):
        meta = orderbook_changes_tx.copy()["meta"].pop("AffectedNodes")
        with self.assertRaises(xrpl.utils.XRPLMetadataException):
            xrpl.utils.ParseOrderBookChanges(metadata=meta)

    def test_no_offers_affected(self):
        actual = xrpl.utils.ParseOrderBookChanges(
            metadata=orderbook_changes_tx_no_offers
        ).all_orderbook_changes
        expected = {}

        self.assertEqual(actual, expected)

    def test_parse_orderbook_changes(self):
        actual = xrpl.utils.ParseOrderBookChanges(
            metadata=orderbook_changes_tx
        ).all_orderbook_changes
        expected = {
            "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo": [
                {
                    "taker_pays": {
                        "final_amount": {
                            "counterparty": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "1018.612178545341",
                    },
                    "taker_gets": {
                        "final_amount": {
                            "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "1023.730832708886",
                    },
                    "sell": True,
                    "sequence": 5811,
                    "status": "filled",
                    "quality": "0",
                    "direction": "sell",
                    "total_received": {
                        "final_amount": {
                            "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "1023.730832708886",
                    },
                    "total_paid": {
                        "final_amount": {
                            "counterparty": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "1018.612178545341",
                    },
                    "account": "rNzgS71DyJPMnWMA8aS7NqvXP7bNuwyaZo",
                }
            ],
            "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A": [
                {
                    "taker_pays": {
                        "final_amount": {
                            "counterparty": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "200",
                    },
                    "taker_gets": {
                        "final_amount": {
                            "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "201",
                    },
                    "sell": True,
                    "sequence": 67701665,
                    "status": "filled",
                    "quality": "0",
                    "direction": "sell",
                    "total_received": {
                        "final_amount": {
                            "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "201",
                    },
                    "total_paid": {
                        "final_amount": {
                            "counterparty": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "currency": "USD",
                            "value": "0",
                        },
                        "previous_value": "200",
                    },
                    "account": "rPu2feBaViWGmWJhvaF5yLocTVD8FUxd2A",
                }
            ],
            "rUqK2eC8TMdm64bJqXMsUcavEbVuWy5Myv": [
                {
                    "taker_pays": {
                        "final_amount": {
                            "counterparty": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "currency": "USD",
                            "value": "62.7598905077505",
                        },
                        "previous_value": "443.8603054033802",
                    },
                    "taker_gets": {
                        "final_amount": {
                            "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "62.8919636313763",
                        },
                        "previous_value": "444.7943735879148",
                    },
                    "sell": True,
                    "sequence": 69051546,
                    "status": "partially-filled",
                    "quality": "0.9979000000000014346825061602",
                    "direction": "sell",
                    "total_received": {
                        "final_amount": {
                            "counterparty": "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq",
                            "currency": "USD",
                            "value": "62.8919636313763",
                        },
                        "previous_value": "444.7943735879148",
                    },
                    "total_paid": {
                        "final_amount": {
                            "counterparty": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                            "currency": "USD",
                            "value": "62.7598905077505",
                        },
                        "previous_value": "443.8603054033802",
                    },
                    "account": "rUqK2eC8TMdm64bJqXMsUcavEbVuWy5Myv",
                }
            ],
        }
        self.assertEqual(actual, expected)
