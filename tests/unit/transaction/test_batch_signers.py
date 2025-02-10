from unittest import TestCase

from xrpl.constants import CryptoAlgorithm, XRPLException
from xrpl.core.binarycodec.main import decode
from xrpl.models.transactions import Batch
from xrpl.models.transactions.batch import BatchSigner
from xrpl.models.transactions.transaction import Transaction
from xrpl.transaction.batch_signers import (
    combine_batch_signers,
    sign_multiaccount_batch,
)
from xrpl.wallet import Wallet

secp_wallet = Wallet.from_seed(
    "spkcsko6Ag3RbCSVXV2FJ8Pd4Zac1",
    algorithm=CryptoAlgorithm.SECP256K1,
)
ed_wallet = Wallet.from_seed(
    "spkcsko6Ag3RbCSVXV2FJ8Pd4Zac1",
    algorithm=CryptoAlgorithm.ED25519,
)
submit_wallet = Wallet.from_seed(
    "sEd7HmQFsoyj5TAm6d98gytM9LJA1MF",
    algorithm=CryptoAlgorithm.ED25519,
)
other_wallet = Wallet.create()


class TestSignMultiAccountBatch(TestCase):
    batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Flags": 1073741824,
                        "Amount": "5000000",
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "Flags": 1073741824,
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "TransactionType": "Batch",
        }
    )

    def test_secp_wallet(self):
        result = sign_multiaccount_batch(secp_wallet, self.batch_tx)
        expected = [
            BatchSigner(
                account="rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                signing_pub_key=(
                    "02691AC5AE1C4C333AE5DF8A93BDC495F0EEBFC6DB0DA7EB6EF80"
                    "8F3AFC006E3FE"
                ),
                txn_signature=(
                    "3045022100EAE8F20550F414DE2EC5501544D17500EFAE6B4B66C36B05BBF59CA"
                    "FDA2C72A502201C9D5C8BEEB6AAC63DC6FB9FEF3E5F008638D36B488E6D98D084"
                    "AC5813E9342A"
                ),
            )
        ]

        self.assertIsNotNone(result.batch_signers)
        self.assertEqual(result.batch_signers, expected)

    def test_ed_wallet(self):
        result = sign_multiaccount_batch(ed_wallet, self.batch_tx)
        expected = [
            BatchSigner(
                account="rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                signing_pub_key=(
                    "ED3CC3D14FD80C213BC92A98AFE13A405A030F845EDCFD5E39528"
                    "6A6E9E62BA638"
                ),
                txn_signature=(
                    "640D96D68C061EF61C5D72460E2254CA74D1CCE75FFC9FF327FC1072419AF474D2"
                    "5A8A01E17AE0BCE71D96B5C5CB87D890D86058A909FB8918DAA046B67EA30C"
                ),
            )
        ]

        self.assertIsNotNone(result.batch_signers)
        self.assertEqual(result.batch_signers, expected)

    def test_not_included_account(self):
        with self.assertRaises(XRPLException):
            sign_multiaccount_batch(other_wallet, self.batch_tx)


class TestCombineBatchSigners(TestCase):
    batch_tx = Batch.from_xrpl(
        {
            "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
            "Flags": 1,
            "LastLedgerSequence": 14973,
            "NetworkID": 21336,
            "RawTransactions": [
                {
                    "RawTransaction": {
                        "Account": "rJy554HmWFFJQGnRfZuoo8nV97XSMq77h7",
                        "Amount": "5000000",
                        "Flags": 1073741824,
                        "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
                {
                    "RawTransaction": {
                        "Account": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                        "Amount": "1000000",
                        "Flags": 1073741824,
                        "Destination": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                        "Fee": "0",
                        "NetworkID": 21336,
                        "Sequence": 0,
                        "SigningPubKey": "",
                        "TransactionType": "Payment",
                    },
                },
            ],
            "Sequence": 215,
            "TransactionType": "Batch",
        }
    )
    tx1 = sign_multiaccount_batch(ed_wallet, batch_tx)
    tx2 = sign_multiaccount_batch(secp_wallet, batch_tx)
    expected_valid = tx1.to_xrpl().get("BatchSigners", []) + tx2.to_xrpl().get(
        "BatchSigners", []
    )

    def test_valid(self):
        result = combine_batch_signers([self.tx1, self.tx2])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_valid_serialized(self):
        result = combine_batch_signers([self.tx1.blob(), self.tx2.blob()])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_valid_sorted(self):
        result = combine_batch_signers([self.tx2, self.tx1])
        self.assertEqual(decode(result)["BatchSigners"], self.expected_valid)

    def test_remove_submitter_signature(self):
        tx = Transaction.from_xrpl(
            {
                "Account": "rJCxK2hX9tDMzbnn3cg1GU2g19Kfmhzxkp",
                "Amount": "1000000",
                "Flags": 1073741824,
                "Destination": "rPMh7Pi9ct699iZUTWaytJUoHcJ7cgyziK",
                "Fee": "0",
                "NetworkID": 21336,
                "Sequence": 0,
                "SigningPubKey": "",
                "TransactionType": "Payment",
            }
        )
        original_dict = self.batch_tx.to_xrpl()
        original_dict["RawTransactions"].append({"RawTransaction": tx.to_xrpl()})

        batch_tx = Batch.from_xrpl(original_dict)
        tx1 = sign_multiaccount_batch(ed_wallet, batch_tx)
        tx2 = sign_multiaccount_batch(secp_wallet, batch_tx)
        tx3 = sign_multiaccount_batch(submit_wallet, batch_tx)

        result = combine_batch_signers([tx1, tx2, tx3])
        expected_valid = tx1.to_xrpl().get("BatchSigners", []) + tx2.to_xrpl().get(
            "BatchSigners", []
        )
        self.assertEqual(decode(result)["BatchSigners"], expected_valid)
