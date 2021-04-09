"""Enum containing the different Transaction types."""

from enum import Enum


class TransactionType(str, Enum):
    """Enum containing the different Transaction types."""

    ACCOUNT_DELETE = "AccountDelete"
    ACCOUNT_SET = "AccountSet"
    CHECK_CANCEL = "CheckCancel"
    CHECK_CASH = "CheckCash"
    CHECK_CREATE = "CheckCreate"
    DEPOSIT_PREAUTH = "DepositPreauth"
    ESCROW_CANCEL = "EscrowCancel"
    ESCROW_CREATE = "EscrowCreate"
    ESCROW_FINISH = "EscrowFinish"
    OFFER_CANCEL = "OfferCancel"
    OFFER_CREATE = "OfferCreate"
    PAYMENT = "Payment"
    PAYMENT_CHANNEL_CLAIM = "PaymentChannelClaim"
    PAYMENT_CHANNEL_CREATE = "PaymentChannelCreate"
    PAYMENT_CHANNEL_FUND = "PaymentChannelFund"
    SET_REGULAR_KEY = "SetRegularKey"
    SIGNER_LIST_SET = "SignerListSet"
    TRUST_SET = "TrustSet"
