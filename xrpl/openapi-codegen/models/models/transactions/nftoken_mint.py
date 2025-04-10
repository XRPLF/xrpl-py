"""Model for NFTokenMint transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.nftoken_mint_flag import NFTokenMintFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenMint(Transaction):
    """
    The NFTokenMint transaction creates a non-fungible token and adds it to the relevant
    NFTokenPage object of the NFTokenMinter as an NFToken object. This transaction is the
    only opportunity the NFTokenMinter has to specify any token fields that are defined as
    immutable (for example, the TokenFlags).
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_MINT,
        init=False
    )

    nf_token_taxon: int = REQUIRED
    """
    An arbitrary taxon, or shared identifier, for a series or collection of related NFTs. To
    mint a series of NFTs, give them all the same taxon.
    """

    issuer: Optional[str] = None
    """
    (Optional) The issuer of the token, if the sender of the account is issuing it on behalf
    of another account. This field must be omitted if the account sending the transaction is
    the issuer of the NFToken. If provided, the issuer's AccountRoot object must have the
    NFTokenMinter field set to the sender of this transaction (this transaction's Account
    field).
    """

    transfer_fee: Optional[int] = None
    """
    (Optional) The value specifies the fee charged by the issuer for secondary sales of the
    NFToken, if such sales are allowed. Valid values for this field are between 0 and 50000
    inclusive, allowing transfer rates of between 0.00% and 50.00% in increments of 0.001.
    If this field is provided, the transaction MUST have the tfTransferable flag enabled.
    """

    uri: Optional[str] = None
    """
    (Optional) Up to 256 bytes of arbitrary data. In JSON, this should be encoded as a
    string of hexadecimal. This is intended to be a URI that points to the data or metadata
    associated with the NFT.
    """

    amount: Optional[Any] = None
    """
    (Optional) Indicates the amount expected or offered for the corresponding NFToken. The
    amount must be non-zero, except where the asset is XRP; then, it is legal to specify an
    amount of zero.
    """

    expiration: Optional[int] = None
    """
    (Optional) Time after which the offer is no longer active, in seconds since the Ripple
    Epoch. Results in an error if the Amount field is not specified.
    """

    destination: Optional[str] = None
    """
    (Optional) If present, indicates that this offer may only be accepted by the specified
    account. Attempts by other accounts to accept this offer MUST fail. Results in an error
    if the Amount field is not specified.
    """

    def _get_errors(self: NFTokenMint) -> Dict[str, str]:
        errors = super._get_errors()
        if self.issuer is not None and self.issuer == self.account:
            errors[NFTokenMint] = "issuer must not be equal to account."
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            self.has_flag(NFTokenMintFlag.TF_TRANSFERABLE) and
            self.transfer_fee is None
        ):
            errors["NFTokenMint"] = "`transfer_fee` must be set with flag `TF_TRANSFERABLE`"
        if self.transfer_fee is not None and self.transfer_fee > 50000:
            errors["NFTokenMint"] = "Field `transfer_fee` must have a value less than or equal to 50000"
        if self.uri is not None and len(self.uri) > 512:
            errors["NFTokenMint"] = "Field `uri` must have a length less than or equal to 512"
        return errors

class NFTokenMintFlagInterface(FlagInterface):
    """
    Enum for NFTokenMint Transaction Flags.
    """

    TF_BURNABLE: bool
    TF_ONLY_XRP: bool
    TF_TRUSTLINE: bool
    TF_TRANSFERABLE: bool

class NFTokenMintFlag(int, Enum):
    """
    Enum for NFTokenMint Transaction Flags.
    """

    TF_BURNABLE = 0x00000001
    """
    Allow the issuer (or an entity authorized by the issuer) to destroy the minted NFToken. (The NFToken&#39;s owner can always do so.)
    """

    TF_ONLY_XRP = 0x00000002
    """
    The minted NFToken can only be bought or sold for XRP.
    """

    TF_TRUSTLINE = 0x00000004
    """
    DEPRECATED Automatically create trust lines from the issuer to hold transfer fees received from transferring the minted NFToken. The fixRemoveNFTokenAutoTrustLine amendment makes it invalid to set this flag.
    """

    TF_TRANSFERABLE = 0x00000008
    """
    The minted NFToken can be transferred to others. If this flag is not enabled, the token can still be transferred from or to the issuer, but a transfer to the issuer must be made based on a buy offer from the issuer and not a sell offer from the NFT holder.
    """


