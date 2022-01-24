from unittest import TestCase

import xrpl.utils

transaction = {
    "Account": "rQ3fNyLjbvcDaPNS4EAJY8aT9zR3uGk17c",
    "Fee": "15",
    "Flags": 0,
    "LastLedgerSequence": 68927248,
    "OfferSequence": 95346038,
    "Sequence": 95346042,
    "SigningPubKey": """
039451ECAC6D4EB75E3C926E7DC7BA7721719A1521502F99EC7EB2FE87CEE9E824
    """,
    "TakerGets": "19328616459",
    "TakerPays": {
        "currency": "CNY",
        "issuer": "rJ1adrpGS3xsnQMb9Cw54tWJVFPuSdZHK",
        "value": "97741.91414225848",
    },
    "TransactionType": "OfferCreate",
    "TxnSignature": """
3045022100C9A7FF07CD398340E18B1E755138A741C16B271BF333F33BA3F823185430A04C022048041A054D096464B99FAF4CB826842179C0E2A96063C2B89FC72B40B74F4FED
    """,
    "date": 695162882,
    "hash": "DB06C0C758E7B88F2E6076A828CD2A14B5B3D26932FEC94309739070FEDF43EF",
    "inLedger": 68927246,
    "ledger_index": 68927246,
    "meta": {
        "AffectedNodes": [
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Flags": 0,
                        "IndexNext": "0",
                        "IndexPrevious": "0",
                        "Owner": "rQ3fNyLjbvcDaPNS4EAJY8aT9zR3uGk17c",
                        "RootIndex": """
07CE63F6E62E095CAF97BC77572A203D75ECB68219F97505AC5DF2DB061C9D96
                        """,
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
07CE63F6E62E095CAF97BC77572A203D75ECB68219F97505AC5DF2DB061C9D96
                    """,
                }
            },
            {
                "CreatedNode": {
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
3F3A8D3CCD47A75938228A58DE8B9DCC074163645C759E83403BCF0C61B9F381
                    """,
                    "NewFields": {
                        "Account": "rQ3fNyLjbvcDaPNS4EAJY8aT9zR3uGk17c",
                        "BookDirectory": """
                        623C4C4AD65873DA787AC85A0A1385FE6233B6DE100799474F11F72DA3EFF025
                        """,
                        "Sequence": 95346042,
                        "TakerGets": "19328616459",
                        "TakerPays": {
                            "currency": "CNY",
                            "issuer": "rJ1adrpGS3xsnQMb9Cw54tWJVFPuSdZHK",
                            "value": "97741.91414225848",
                        },
                    },
                },
            },
            {
                "ModifiedNode": {
                    "FinalFields": {
                        "Account": "rQ3fNyLjbvcDaPNS4EAJY8aT9zR3uGk17c",
                        "Balance": "5006015759",
                        "Flags": 0,
                        "OwnerCount": 5,
                        "Sequence": 95346043,
                    },
                    "LedgerEntryType": "AccountRoot",
                    "LedgerIndex": """
47FE64F9223D604034486F4DA7A175D5DA7F8A096952261CF8F3D77B74DC4AFA
                    """,
                    "PreviousFields": {
                        "Balance": "5006015774",
                        "Sequence": 95346042,
                    },
                    "PreviousTxnID": """
8DF74066B104F9D01BA2CE0B8F5B9746838746836A9240D349B336DB8EB7FB8C
                    """,
                    "PreviousTxnLgrSeq": 68927246,
                }
            },
            {
                "CreatedNode": {
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
623C4C4AD65873DA787AC85A0A1385FE6233B6DE100799474F11F72DA3EFF025
                    """,
                    "NewFields": {
                        "ExchangeRate": "4f11f72da3eff025",
                        "RootIndex": """
623C4C4AD65873DA787AC85A0A1385FE6233B6DE100799474F11F72DA3EFF025
                        """,
                        "TakerPaysCurrency": "000000000000000000000000434E590000000000",
                        "TakerPaysIssuer": "0360E3E0751BD9A566CD03FA6CAFC78118B82BA0",
                    },
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "ExchangeRate": "4f11faf6376ace8b",
                        "Flags": 0,
                        "RootIndex": """
623C4C4AD65873DA787AC85A0A1385FE6233B6DE100799474F11FAF6376ACE8B
                        """,
                        "TakerGetsCurrency": "0000000000000000000000000000000000000000",
                        "TakerGetsIssuer": "0000000000000000000000000000000000000000",
                        "TakerPaysCurrency": "000000000000000000000000434E590000000000",
                        "TakerPaysIssuer": "0360E3E0751BD9A566CD03FA6CAFC78118B82BA0",
                    },
                    "LedgerEntryType": "DirectoryNode",
                    "LedgerIndex": """
623C4C4AD65873DA787AC85A0A1385FE6233B6DE100799474F11FAF6376ACE8B
                    """,
                },
            },
            {
                "DeletedNode": {
                    "FinalFields": {
                        "Account": "rQ3fNyLjbvcDaPNS4EAJY8aT9zR3uGk17c",
                        "BookDirectory": """
623C4C4AD65873DA787AC85A0A1385FE6233B6DE100799474F11FAF6376ACE8B
                        """,
                        "BookNode": "0",
                        "Flags": 0,
                        "OwnerNode": "0",
                        "PreviousTxnID": """
14969DAE920168234566DCDCED5C6CE713E32E46C1C2105CEB27AFB0278D240E
                        """,
                        "PreviousTxnLgrSeq": 68927245,
                        "Sequence": 95346038,
                        "TakerGets": "593588370",
                        "TakerPays": {
                            "currency": "CNY",
                            "issuer": "rJ1adrpGS3xsnQMb9Cw54tWJVFPuSdZHK",
                            "value": "3004.156678072142",
                        },
                    },
                    "LedgerEntryType": "Offer",
                    "LedgerIndex": """
752BF07F08EBF7144E9DCE58A7D9B42F5CE2C5EB20A0722C0CA37E61A8503873
                    """,
                },
            },
        ],
        "TransactionIndex": 26,
        "TransactionResult": "tesSUCCESS",
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
