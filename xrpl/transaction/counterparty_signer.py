"""Helper functions for signing LoanSet transactions as the counterparty."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from xrpl.constants import XRPLException
from xrpl.core.addresscodec import (
    decode_classic_address,
    is_valid_xaddress,
    xaddress_to_classic_address,
)
from xrpl.core.binarycodec import encode, encode_for_multisigning, encode_for_signing
from xrpl.core.keypairs import sign as keypairs_sign
from xrpl.models.transactions import LoanSet, Transaction
from xrpl.models.transactions.loan_set import CounterpartySignature
from xrpl.models.transactions.transaction import Signer
from xrpl.wallet import Wallet


def compute_signature(
    tx_json: Dict[str, Any],
    private_key: str,
    sign_as: Optional[str] = None,
) -> str:
    """
    Signs a transaction with the proper signing encoding.

    Args:
        tx_json: A transaction JSON to sign.
        private_key: A key to sign the transaction with.
        sign_as: Multisign only. An account address to include in the Signer field.
            Can be either a classic address or an XAddress.

    Returns:
        A signed transaction signature in hex format.
    """
    if sign_as:
        classic_address = (
            xaddress_to_classic_address(sign_as)[0]
            if is_valid_xaddress(sign_as)
            else sign_as
        )
        return keypairs_sign(
            bytes.fromhex(encode_for_multisigning(tx_json, classic_address)),
            private_key,
        )
    return keypairs_sign(
        bytes.fromhex(encode_for_signing(tx_json)),
        private_key,
    )


@dataclass
class SignLoanSetResult:
    """Result of signing a LoanSet transaction by the counterparty."""

    tx: LoanSet
    tx_blob: str
    hash: str


@dataclass
class CombineLoanSetResult:
    """Result of combining LoanSet counterparty signatures."""

    tx: LoanSet
    tx_blob: str


def sign_loan_set_by_counterparty(
    wallet: Wallet,
    transaction: Union[LoanSet, str],
    multisign: Union[bool, str] = False,
) -> SignLoanSetResult:
    """
    Signs a LoanSet transaction as the counterparty.

    This function adds a counterparty signature to a LoanSet transaction that has
    already been signed by the first party. The counterparty uses their wallet to
    sign the transaction, which is required for multi-party loan agreements on the
    XRP Ledger.

    Args:
        wallet: The counterparty's wallet used for signing the transaction.
        transaction: The LoanSet transaction to sign. Can be either:
            - A LoanSet transaction object that has been signed by the first party
            - A serialized transaction blob (string) in hex format
        multisign: Specify True/False to use multisign or actual address
            (classic/x-address) to make multisign tx request.
            The actual address is only needed in the case of regular key usage.

    Returns:
        A SignLoanSetResult containing:
            - tx: The signed LoanSet transaction object
            - tx_blob: The serialized transaction blob (hex string) ready to submit
            - hash: The transaction hash (useful for tracking the transaction)

    Raises:
        XRPLException: If:
            - The transaction is not a LoanSet transaction
            - The transaction fails validation checks
            - The transaction is already signed by the counterparty
            - The transaction has not been signed by the first party yet
    """
    # Decode transaction if it's a blob
    if isinstance(transaction, str):
        tx = Transaction.from_blob(transaction)
    else:
        tx = transaction

    # Validate transaction type
    if tx.transaction_type.value != "LoanSet":
        raise XRPLException("Transaction must be a LoanSet transaction.")

    # Cast to LoanSet after validation
    loan_set_tx = tx if isinstance(tx, LoanSet) else LoanSet.from_xrpl(tx.to_xrpl())

    # Validate the LoanSet transaction fields
    try:
        loan_set_tx.validate()
    except Exception as e:
        raise XRPLException(str(e)) from e

    # Validate not already signed by counterparty
    if loan_set_tx.counterparty_signature is not None:
        raise XRPLException("Transaction is already signed by the counterparty.")

    # Validate first party has signed
    if loan_set_tx.txn_signature is None or loan_set_tx.signing_pub_key is None:
        raise XRPLException("Transaction must be first signed by first party.")

    # Determine multisign address
    multisign_address: Optional[str] = None
    if isinstance(multisign, str):
        multisign_address = multisign
    elif multisign:
        multisign_address = wallet.address

    # Prepare transaction JSON for signing
    tx_json = loan_set_tx.to_xrpl()

    # Sign and add counterparty signature
    if multisign_address:
        # Convert X-Address to classic address if needed
        classic_address = (
            xaddress_to_classic_address(multisign_address)[0]
            if is_valid_xaddress(multisign_address)
            else multisign_address
        )
        signature = compute_signature(tx_json, wallet.private_key, multisign_address)
        tx_json["CounterpartySignature"] = {
            "Signers": [
                {
                    "Signer": {
                        "Account": classic_address,
                        "SigningPubKey": wallet.public_key,
                        "TxnSignature": signature,
                    }
                }
            ]
        }
    else:
        signature = compute_signature(tx_json, wallet.private_key)
        tx_json["CounterpartySignature"] = {
            "SigningPubKey": wallet.public_key,
            "TxnSignature": signature,
        }

    # Create the signed transaction
    signed_tx = LoanSet.from_xrpl(tx_json)
    serialized = encode(tx_json)

    return SignLoanSetResult(
        tx=signed_tx,
        tx_blob=serialized,
        hash=signed_tx.get_hash(),
    )


def combine_loanset_counterparty_signers(
    transactions: List[Union[LoanSet, str]],
) -> CombineLoanSetResult:
    """
    Combines multiple LoanSet transactions signed by the counterparty into a
    single transaction.

    Args:
        transactions: An array of signed LoanSet transactions (in object or blob
            form) to combine.

    Returns:
        A CombineLoanSetResult containing:
            - tx: The combined LoanSet transaction object
            - tx_blob: The serialized transaction blob (hex string) ready to submit

    Raises:
        XRPLException: If:
            - There are no transactions to combine
            - Any of the transactions are not LoanSet transactions
            - Any of the transactions do not have Signers in CounterpartySignature
            - Any of the transactions do not have a first party signature
            - The transactions are not identical (except for Signers)
    """
    if len(transactions) == 0:
        raise XRPLException("There are 0 transactions to combine.")

    # Decode all transactions
    decoded_transactions: List[LoanSet] = []
    for tx_or_blob in transactions:
        if isinstance(tx_or_blob, str):
            tx = Transaction.from_blob(tx_or_blob)
        else:
            tx = tx_or_blob

        # Validate transaction type
        if tx.transaction_type.value != "LoanSet":
            raise XRPLException("Transaction must be a LoanSet transaction.")

        loan_set_tx = tx if isinstance(tx, LoanSet) else LoanSet.from_xrpl(tx.to_xrpl())

        # Validate CounterpartySignature has Signers
        if (
            loan_set_tx.counterparty_signature is None
            or loan_set_tx.counterparty_signature.signers is None
            or len(loan_set_tx.counterparty_signature.signers) == 0
        ):
            raise XRPLException("CounterpartySignature must have Signers.")

        # Validate first party has signed
        if loan_set_tx.txn_signature is None or loan_set_tx.signing_pub_key is None:
            raise XRPLException("Transaction must be first signed by first party.")

        decoded_transactions.append(loan_set_tx)

    # Validate all transactions are identical (except for Signers)
    _validate_loanset_transaction_equivalence(decoded_transactions)

    # Combine all signers
    combined_tx = _get_transaction_with_all_counterparty_signers(decoded_transactions)

    return CombineLoanSetResult(
        tx=combined_tx,
        tx_blob=encode(combined_tx.to_xrpl()),
    )


def _validate_loanset_transaction_equivalence(transactions: List[LoanSet]) -> None:
    """
    Validates that all transactions are identical except for CounterpartySignature.

    Args:
        transactions: List of LoanSet transactions to validate.

    Raises:
        XRPLException: If transactions are not identical.
    """
    if len(transactions) <= 1:
        return

    # Get the first transaction without CounterpartySignature.Signers for comparison
    example_tx_dict = transactions[0].to_xrpl()
    if "CounterpartySignature" in example_tx_dict:
        example_tx_dict["CounterpartySignature"] = {
            **example_tx_dict["CounterpartySignature"],
            "Signers": None,
        }

    for tx in transactions[1:]:
        tx_dict = tx.to_xrpl()
        if "CounterpartySignature" in tx_dict:
            tx_dict["CounterpartySignature"] = {
                **tx_dict["CounterpartySignature"],
                "Signers": None,
            }

        if tx_dict != example_tx_dict:
            raise XRPLException("Transactions are not identical.")


def _get_transaction_with_all_counterparty_signers(
    transactions: List[LoanSet],
) -> LoanSet:
    """
    Combines all CounterpartySignature.Signers from the transactions into one.

    Args:
        transactions: List of LoanSet transactions with CounterpartySignature.Signers.

    Returns:
        A LoanSet transaction with all Signers combined and sorted.
    """
    # Collect all signers from all transactions
    all_signers: List[Signer] = []
    for tx in transactions:
        if (
            tx.counterparty_signature is not None
            and tx.counterparty_signature.signers is not None
        ):
            all_signers.extend(tx.counterparty_signature.signers)

    # Sort signers by account address (as per XRPL requirements)
    all_signers.sort(key=lambda signer: decode_classic_address(signer.account))

    # Create new transaction with combined signers
    tx_dict = transactions[0].to_dict()
    tx_dict["counterparty_signature"] = CounterpartySignature(signers=all_signers)

    return LoanSet.from_dict(tx_dict)
