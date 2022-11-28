"""Multisign transaction methods with XRPL transactions."""
from typing import List

from xrpl.core.binarycodec import decode, encode, encode_for_multisigning
from xrpl.core.keypairs.main import sign
from xrpl.models.transactions.transaction import Signer, Transaction
from xrpl.wallet.main import Wallet


async def sign_for_multisign(
    transaction: Transaction,
    wallet: Wallet,
) -> str:
    """
    Signs a transaction to be used for multisigning.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    signature = sign(
        bytes.fromhex(
            encode_for_multisigning(
                transaction.to_xrpl(),
                wallet.classic_address,
            )
        ),
        wallet.private_key,
    )

    tx_dict = transaction.to_dict()
    tx_dict["signers"] = [
        Signer(
            account=wallet.classic_address,
            txn_signature=signature,
            signing_pub_key=wallet.public_key,
        )
    ]

    return encode(Transaction.from_dict(tx_dict).to_xrpl())


async def multisign(transaction: Transaction, tx_blobs: List[str]) -> Transaction:
    """
    Takes several transactions with Signer fields (blob form) and creates a
    single transaction with all Signers that then gets signed and returned.

    Args:
        transaction: the transaction to be multisigned.
        tx_blobs: a list of signed transactions (in blob form) to combine into
            a single signed transaction.

    Returns:
        The multisigned transaction.
    """
    decoded_tx_blobs_signers = [
        decode(tx_blob)["Signers"][0]["Signer"] for tx_blob in tx_blobs
    ]

    tx_dict = transaction.to_dict()
    tx_dict["signers"] = [
        Signer(
            account=decoded_tx_blobs_signer["Account"],
            txn_signature=decoded_tx_blobs_signer["TxnSignature"],
            signing_pub_key=decoded_tx_blobs_signer["SigningPubKey"],
        )
        for decoded_tx_blobs_signer in decoded_tx_blobs_signers
    ]

    return Transaction.from_dict(tx_dict)
