"""Helper functions for order book parser."""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Literal

from xrpl.models import TransactionMetadata
from xrpl.utils.time_conversions import ripple_time_to_posix
from xrpl.utils.txn_parser.utils import NormalizedNode, normalize_nodes
from xrpl.utils.txn_parser.utils.parser import get_value, group_by_account
from xrpl.utils.txn_parser.utils.types import (
    AccountOfferChange,
    AccountOfferChanges,
    CurrencyAmount,
    OfferChange,
)
from xrpl.utils.xrp_conversions import drops_to_xrp

LSF_SELL = 0x00020000


def _get_offer_status(
    node: NormalizedNode,
) -> Literal["created", "partially-filled", "filled", "cancelled"]:
    node_type = node["NodeType"]
    if node_type == "CreatedNode":
        return "created"
    elif node_type == "ModifiedNode":
        return "partially-filled"
    else:  # node_type == "DeletedNode"
        previous_fields = node.get("PreviousFields")
        # a filled offer has previous fields
        if previous_fields is not None:
            return "filled"
        # a cancelled offer has no previous fields
        return "cancelled"


def _derive_currency_amount(
    currency_amount: Union[str, Dict[str, str]]
) -> CurrencyAmount:
    if isinstance(currency_amount, str):
        return CurrencyAmount(currency="XRP", value=str(drops_to_xrp(currency_amount)))
    else:
        return CurrencyAmount(
            currency=currency_amount["currency"],
            issuer=currency_amount["issuer"],
            value=currency_amount["value"],
        )


def _calculate_delta(
    final_amount: CurrencyAmount,
    previous_amount: CurrencyAmount,
) -> str:
    final_value = get_value(final_amount)
    previous_value = get_value(previous_amount)
    delta = final_value - previous_value
    return str(delta.copy_abs())


def _get_change_amount(
    node: NormalizedNode,
    status: Literal["created", "partially-filled", "filled", "cancelled"],
    side: Literal["TakerGets", "TakerPays"],
) -> Optional[CurrencyAmount]:
    if status == "cancelled":
        final_fields = node.get("FinalFields")
        if final_fields is not None:
            final_fields_amount = final_fields.get(side)
            if final_fields_amount is not None:
                return _derive_currency_amount(final_fields_amount)
    if status == "created":
        new_fields = node.get("NewFields")
        if new_fields is not None:
            new_fields_amount = new_fields.get(side)
            if new_fields_amount is not None:
                return _derive_currency_amount(new_fields_amount)
    final_fields = node.get("FinalFields")
    previous_fields = node.get("PreviousFields")
    if final_fields is not None and previous_fields is not None:
        final_fields_amount = final_fields.get(side)
        previous_fields_amount = previous_fields.get(side)
        if final_fields_amount is not None and previous_fields_amount is not None:
            final_amount = _derive_currency_amount(final_fields_amount)
            previous_amount = _derive_currency_amount(previous_fields_amount)
            value = _calculate_delta(final_amount, previous_amount)
            # final_amount is being reused because it makes
            # it easier to return the changed amount.
            final_amount["value"] = value
            # From now on you could consider final_amount as changed_amount.
            return final_amount
    return None


def _get_quality(
    taker_gets: CurrencyAmount,
    taker_pays: CurrencyAmount,
    book_directory: str,
) -> str:
    quality_hex = book_directory[-16:]  # last 16 characters of the BookDirectory
    taker_gets_currency = taker_gets["currency"]
    taker_pays_currency = taker_pays["currency"]
    mantissa = float.fromhex(quality_hex[2:])
    offset = int(quality_hex[:2], 16) - 100
    scientific_quality = "{:.16f}e{}".format(mantissa, offset)
    quality = Decimal(scientific_quality)
    if taker_gets_currency == "XRP" or taker_pays_currency == "XRP":
        quality = quality * 1000000
    return str(quality.normalize())


def _get_optional_fields(
    node: NormalizedNode,
    field_name: str,
) -> Optional[Any]:
    new_fields = node.get("NewFields")
    final_fields = node.get("FinalFields")
    if new_fields is not None:
        return new_fields.get(field_name)
    if final_fields is not None:
        return final_fields.get(field_name)
    return None


def _get_fields(
    node: NormalizedNode,
    field_name: str,
) -> Optional[Any]:
    new_fields = node.get("NewFields")
    final_fields = node.get("FinalFields")
    if new_fields is not None:
        return new_fields.get(field_name)
    if final_fields is not None:
        return final_fields.get(field_name)
    return None


def _get_offer_change(node: NormalizedNode) -> Optional[AccountOfferChange]:
    status = _get_offer_status(node)
    taker_gets = _get_change_amount(node, status, "TakerGets")
    taker_pays = _get_change_amount(node, status, "TakerPays")
    account = _get_fields(node, "Account")
    sequence = _get_fields(node, "Sequence")
    book_directory = _get_fields(node, "BookDirectory")
    # if required fields are None return None
    if (
        taker_gets is None
        or taker_pays is None
        or account is None
        or sequence is None
        or book_directory is None
    ):
        return None
    expiration_time = _get_fields(node, "Expiration")
    flags = _get_fields(node, "Flags")
    direction: Literal["buy", "sell"] = (
        "sell" if (flags is not None and flags & LSF_SELL != 0) else "buy"
    )
    quality = _get_quality(taker_gets, taker_pays, book_directory)
    quantity = taker_pays if direction == "buy" else taker_gets
    total_price = taker_gets if direction == "buy" else taker_pays
    offer_change = OfferChange(
        direction=direction,
        quantity=quantity,
        total_price=total_price,
        sequence=sequence,
        status=status,
        maker_exchange_rate=quality,
    )
    if expiration_time is not None:
        offer_change["expiration_time"] = ripple_time_to_posix(expiration_time)
    return AccountOfferChange(account=account, offer_change=offer_change)


def _group_offer_changes_by_account(
    account_offer_changes: List[AccountOfferChange],
) -> List[AccountOfferChanges]:
    grouped_offer_changes = group_by_account(account_offer_changes)
    result = []
    for account, account_obj in grouped_offer_changes.items():
        offer_changes: List[OfferChange] = [
            offer_change["offer_change"] for offer_change in account_obj
        ]
        result.append(
            AccountOfferChanges(
                account=account,
                offer_changes=offer_changes,
            )
        )
    return result


def compute_order_book_changes(
    metadata: TransactionMetadata,
) -> List[AccountOfferChanges]:
    """
    Compute the offer changes from offer objects affected by the transaction.

    Args:
        metadata: Transactions metadata.

    Returns:
        All offer changes caused by the transaction.
        The offer changes are grouped by their owner accounts.
    """
    normalized_nodes = normalize_nodes(metadata)
    offer_nodes = [
        node for node in normalized_nodes if node["LedgerEntryType"] == "Offer"
    ]
    offer_changes = []
    for node in offer_nodes:
        change = _get_offer_change(node)
        if change is not None:
            offer_changes.append(change)
    return _group_offer_changes_by_account(offer_changes)
