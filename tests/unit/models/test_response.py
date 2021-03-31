import warnings
from unittest import TestCase

from xrpl.models.response import Response, ResponseStatus


class TestResponse(TestCase):
    def test_is_successful_true(self):
        response = Response(status=ResponseStatus.SUCCESS, result={})
        self.assertTrue(response.is_successful())

    def test_is_successful_false(self):
        response = Response(status=ResponseStatus.ERROR, result={})
        self.assertFalse(response.is_successful())

    def test_doesnt_warn_when_wrapping_non_payment(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Response(status=ResponseStatus.SUCCESS, result={})
            self.assertTrue(len(w) == 0)

    def test_doesnt_warn_when_wrapping_non_partial_payment(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Response(
                status=ResponseStatus.SUCCESS,
                result={
                    "accepted": True,
                    "account_sequence_available": 16204432,
                    "account_sequence_next": 16204432,
                    "applied": True,
                    "broadcast": True,
                    "engine_result": "tesSUCCESS",
                    "engine_result_code": 0,
                    "engine_result_message": "The transaction was applied. "
                    "Only final in a validated ledger.",
                    "kept": True,
                    "open_ledger_cost": "10",
                    "queued": False,
                    "tx_blob": "12000022000000002400F7428F6140000000000000"
                    "0A68400000000000000A7321036ECC359C57864ED4E63FA61"
                    "C06378D796DA771A38AF87E25835EEF786E95920E74463044"
                    "02204C89A39D433AB6F77D43FB048405C6EF06F596E2133CC"
                    "1FE866494AED9D633EB02203736CB025BC6C4AB34567A08D9"
                    "F7D14361351827CD56147BDE4DC9A38A5E0FA98114D1BC9E7"
                    "D2286F0AD142A7269F45AAC3C198230A083148ABCE81E5030"
                    "B036C3E01D8064845235C6E3BFD8",
                    "tx_json": {
                        "Account": "rLfzB272tRBrP7LrJuhCcQk8vuKAFQyxVU",
                        "Amount": "10",
                        "Destination": "rDe2YA2qpfDiiQen1v5hfEvJQ61H8zWBqA",
                        "Fee": "10",
                        "Flags": 0,
                        "Sequence": 16204431,
                        "SigningPubKey": "036ECC359C57864ED4E63FA61C06378D7"
                        "96DA771A38AF87E25835EEF786E95920E",
                        "TransactionType": "Payment",
                        "TxnSignature": "304402204C89A39D433AB6F77D43FB0484"
                        "05C6EF06F596E2133CC1FE866494AED9D633EB02203736"
                        "CB025BC6C4AB34567A08D9F7D14361351827CD56147BDE"
                        "4DC9A38A5E0FA9",
                        "hash": "1CD3C4813C93C7BC1F58842C5B8F1B868ADBA55BEB"
                        "80622022ADB5D4F1602606",
                    },
                    "validated_ledger_index": 16204443,
                },
            )
            self.assertTrue(len(w) == 0)

    def test_warns_when_wrapping_partial_payment(self):
        with self.assertWarns(Warning):
            Response(
                status=ResponseStatus.SUCCESS,
                result={
                    "Account": "rhYNUQadhC66NwqaJwQiZj5Lz8qQpaSyjK",
                    "Amount": {
                        "currency": "USD",
                        "issuer": "rhYNUQadhC66NwqaJwQiZj5Lz8qQpaSyjK",
                        "value": "1",
                    },
                    "Destination": "rDJ8XRBdpjwjVkTUL9y4WN4dNSdjwW8YWk",
                    "Fee": "10",
                    "Flags": 131072,
                    "LastLedgerSequence": 16204561,
                    "SendMax": {
                        "currency": "USD",
                        "issuer": "rhYNUQadhC66NwqaJwQiZj5Lz8qQpaSyjK",
                        "value": "10",
                    },
                    "Sequence": 16204551,
                    "SigningPubKey": "035E3E5F834CBD62A40693F1BEC707257"
                    "69760544DFEC0999EC9F7903D19B8D08E",
                    "TransactionType": "Payment",
                    "TxnSignature": "3045022100B0FA52C054EEE7278308D3DC"
                    "3CF7156B8F86C7188BA27159BEEACA86402EE389022035"
                    "35B8E79E40B11BA81AE66401088680B5E0EAC1801362BF"
                    "08B51C862F0ABA92",
                    "date": 670437812,
                    "hash": "DA67B40E0A0C1BF80863CE9FC1F7CE1AB0935583EF"
                    "A653486EFD0B95D5904F6C",
                    "inLedger": 16204557,
                    "ledger_index": 16204557,
                    "meta": {
                        "AffectedNodes": [
                            {
                                "ModifiedNode": {
                                    "FinalFields": {
                                        "Balance": {
                                            "currency": "USD",
                                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                                            "value": "-1",
                                        },
                                        "Flags": 3276800,
                                        "HighLimit": {
                                            "currency": "USD",
                                            "issuer": "rDJ8XRBdpjwjVkTUL"
                                            "9y4WN4dNSdjwW8YWk",
                                            "value": "100",
                                        },
                                        "HighNode": "0000000000000000",
                                        "LowLimit": {
                                            "currency": "USD",
                                            "issuer": "rhYNUQadhC66NwqaJ"
                                            "wQiZj5Lz8qQpaSyjK",
                                            "value": "0",
                                        },
                                        "LowNode": "0000000000000000",
                                    },
                                    "LedgerEntryType": "RippleState",
                                    "LedgerIndex": "6F5EA6F8E556B1D2296461B3D7"
                                    "7AD18F510246A26759BF61E39507E3453D315C",
                                    "PreviousFields": {
                                        "Balance": {
                                            "currency": "USD",
                                            "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                                            "value": "0",
                                        }
                                    },
                                    "PreviousTxnID": "7C87A9454ABF0441B15B8A57A"
                                    "7A24AF68164378B6281100B4D7F4C82E54BB8C8",
                                    "PreviousTxnLgrSeq": 16204555,
                                }
                            },
                            {
                                "ModifiedNode": {
                                    "FinalFields": {
                                        "Account": "rhYNUQadhC66NwqaJwQiZj5Lz8qQpaSyjK",
                                        "Balance": "999999949",
                                        "Flags": 0,
                                        "OwnerCount": 2,
                                        "Sequence": 16204552,
                                    },
                                    "LedgerEntryType": "AccountRoot",
                                    "LedgerIndex": "F7B2E8C6D2E400FEC1710144887447"
                                    "FE62FCF1C84873E1CD532F238AD7AE7BF7",
                                    "PreviousFields": {
                                        "Balance": "999999959",
                                        "Sequence": 16204551,
                                    },
                                    "PreviousTxnID": "FB2E845133983E947469F698173A"
                                    "96C9F25B8135DA163D16DBA733BAED9832FA",
                                    "PreviousTxnLgrSeq": 16204555,
                                }
                            },
                        ],
                        "TransactionIndex": 0,
                        "TransactionResult": "tesSUCCESS",
                        "delivered_amount": {
                            "currency": "USD",
                            "issuer": "rhYNUQadhC66NwqaJwQiZj5Lz8qQpaSyjK",
                            "value": "1",
                        },
                    },
                    "validated": True,
                },
            )
