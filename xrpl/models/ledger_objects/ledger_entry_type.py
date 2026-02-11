"""Enum for ledger entry types on the XRP Ledger."""

from enum import Enum


class LedgerEntryType(str, Enum):
    """Enum representing ledger entry types on the XRP Ledger."""

    ACCOUNT_ROOT = "AccountRoot"
    """An AccountRoot ledger entry describes a single account."""

    AMENDMENTS = "Amendments"
    """The Amendments ledger entry tracks the status of amendments."""

    AMM = "AMM"
    """An AMM ledger entry describes an Automated Market Maker instance."""

    BRIDGE = "Bridge"
    """A Bridge ledger entry describes a cross-chain bridge."""

    CHECK = "Check"
    """A Check ledger entry describes a check."""

    CREDENTIAL = "Credential"
    """A Credential ledger entry describes a credential."""

    DELEGATE = "Delegate"
    """A Delegate ledger entry describes delegation permissions."""

    DEPOSIT_PREAUTH = "DepositPreauth"
    """A DepositPreauth ledger entry tracks preauthorization for payments."""

    DIRECTORY_NODE = "DirectoryNode"
    """A DirectoryNode ledger entry represents a page in a directory."""

    DID = "DID"
    """A DID ledger entry describes a decentralized identifier."""

    ESCROW = "Escrow"
    """An Escrow ledger entry describes an escrow."""

    FEE_SETTINGS = "FeeSettings"
    """The FeeSettings ledger entry contains the current base transaction cost and reserve amounts."""

    LEDGER_HASHES = "LedgerHashes"
    """A LedgerHashes ledger entry contains hashes of previous ledgers."""

    LOAN = "Loan"
    """A Loan ledger entry describes a loan."""

    LOAN_BROKER = "LoanBroker"
    """A LoanBroker ledger entry describes a loan broker."""

    MPTOKEN = "MPToken"
    """An MPToken ledger entry describes a multi-purpose token."""

    MPTOKEN_ISSUANCE = "MPTokenIssuance"
    """An MPTokenIssuance ledger entry describes a multi-purpose token issuance."""

    NEGATIVE_UNL = "NegativeUNL"
    """The NegativeUNL ledger entry contains the current negative UNL."""

    NFTOKEN_OFFER = "NFTokenOffer"
    """An NFTokenOffer ledger entry describes an offer to buy or sell an NFToken."""

    NFTOKEN_PAGE = "NFTokenPage"
    """An NFTokenPage ledger entry contains a collection of NFTokens owned by the same account."""

    OFFER = "Offer"
    """An Offer ledger entry describes an offer to exchange currencies."""

    ORACLE = "Oracle"
    """An Oracle ledger entry describes a price oracle."""

    PAY_CHANNEL = "PayChannel"
    """A PayChannel ledger entry describes a payment channel."""

    PERMISSIONED_DOMAIN = "PermissionedDomain"
    """A PermissionedDomain ledger entry describes a permissioned domain."""

    RIPPLE_STATE = "RippleState"
    """A RippleState ledger entry describes a trust line between two accounts."""

    SIGNER_LIST = "SignerList"
    """A SignerList ledger entry describes a list of signers for multi-signing."""

    SPONSORSHIP = "Sponsorship"
    """A Sponsorship ledger entry describes a sponsorship relationship between two accounts."""

    TICKET = "Ticket"
    """A Ticket ledger entry represents a sequence number set aside for future use."""

    VAULT = "Vault"
    """A Vault ledger entry describes a vault."""

    XCHAIN_OWNED_CLAIM_ID = "XChainOwnedClaimID"
    """An XChainOwnedClaimID ledger entry represents a cross-chain claim ID."""

    XCHAIN_OWNED_CREATE_ACCOUNT_CLAIM_ID = "XChainOwnedCreateAccountClaimID"
    """An XChainOwnedCreateAccountClaimID ledger entry represents a cross-chain create account claim ID."""

