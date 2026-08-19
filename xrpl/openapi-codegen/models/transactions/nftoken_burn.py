"""Model for NFTokenBurn transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenBurn(Transaction):
    """
    The NFTokenBurn transaction is used to remove a NFToken object from the NFTokenPage in
    which it is being held, effectively removing the token from the ledger (burning it).
    The sender of this transaction must be the owner of the NFToken to burn; or, if the
    NFToken has the lsfBurnable flag enabled, can be the issuer or the issuer's authorized
    NFTokenMinter account instead.  If this operation succeeds, the corresponding NFToken is
    removed. If this operation empties the NFTokenPage holding the NFToken or results in
    consolidation, thus removing a NFTokenPage, the owner’s reserve requirement is reduced
    by one.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_BURN, init=False
    )

    nf_token_id: str = REQUIRED
    """
    The NFToken to be removed by this transaction.
    """

    owner: Optional[str] = None
    """
    (Optional) The owner of the NFToken to burn. Only used if that owner is different than
    the account sending this transaction. The issuer or authorized minter can use this field
    to burn NFTs that have the lsfBurnable flag enabled.
    """
