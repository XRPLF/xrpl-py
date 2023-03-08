"""Utils to get an NFTokenID from metadata"""
from typing import List, Optional, TypedDict, Union, cast

from typing_extensions import TypeAlias, TypeGuard

from xrpl.models.ledger.nft import NFToken
from xrpl.models.transactions.metadata import (
    CreatedNode,
    DeletedNode,
    ModifiedNode,
    TransactionMetadata,
)


# TODO: Add dynamic typing on the return type
def flatmap(func, objects):
    """
    Flattens objects into a single list, and applies func to every object in objects.

    Source: https://dev.to/turbaszek/flat-map-in-python-3g98

    Args:
        func: A function to apply to every object.
        objects: A list of lists to be flattened and updated.
    """
    return [updated_object for object in objects for updated_object in func(object)]


Node: TypeAlias = Union[CreatedNode, ModifiedNode, DeletedNode]


def isCreatedNode(node: Node) -> TypeGuard[CreatedNode]:
    """
    Typeguard for CreatedNode

    Args:
        node: A node of any type (CreatedNode, ModifiedNode, or DeletedNode)

    Returns:
        Whether this node is a CreatedNode.
    """
    return "CreatedNode" in node


def isModifiedNode(node: Node) -> TypeGuard[ModifiedNode]:
    """
    Typeguard for ModifiedNode

    Args:
        node: A node of any type (CreatedNode, ModifiedNode, or DeletedNode)

    Returns:
        Whether this node is a ModifiedNode.
    """
    return "ModifiedNode" in node


def isDeletedNode(node: Node) -> TypeGuard[DeletedNode]:
    """
    Typeguard for DeletedNode

    Args:
        node: A node of any type (CreatedNode, ModifiedNode, or DeletedNode)

    Returns:
        Whether this node is a DeletedNode.
    """
    return "DeletedNode" in node


def get_nftoken_ids_from_nftokens(nftokens: List[NFToken]) -> List[str]:
    """
    Extract NFTokenIDs from a list of NFTokens.

    Args:
        nftokens: A list of NFTokens

    Returns:
        A list of NFTokenIDs.
    """
    return [
        id
        for id in [token["NFToken"]["NFTokenID"] for token in nftokens]
        if id is not None
    ]


def get_nftoken_id(meta: TransactionMetadata) -> str:
    """
    Gets the NFTokenID for an NFT recently minted with NFTokenMint.

    Args:
        meta: Metadata from the response to submitting an NFTokenMint transaction.

    Returns:
        The newly minted NFToken's NFTokenID.

    Raises:
        TypeError: if given something other than metadata (e.g. the full
                    transaction response).
    """
    if meta is None or meta.get("AffectedNodes") is None:
        raise TypeError(
            f"""Unable to parse the parameter given to get_nftoken_id.
            'meta' must be the metadata from an NFTokenMint transaction.
            Received {meta} instead."""
        )

    """
    * When a mint results in splitting an existing page,
    * it results in a created page and a modified node. Sometimes,
    * the created node needs to be linked to a third page, resulting
    * in modifying that third page's PreviousPageMin or NextPageMin
    * field changing, but no NFTs within that page changing. In this
    * case, there will be no previous NFTs and we need to skip.
    * However, there will always be NFTs listed in the final fields,
    * as rippled outputs all fields in final fields even if they were
    * not changed. Thus why we add the additional condition to check
    * if the PreviousFields contains NFTokens
    """

    def has_nftoken_page(node: Union[CreatedNode, ModifiedNode, DeletedNode]) -> bool:
        if isCreatedNode(node):
            return node["CreatedNode"]["LedgerEntryType"] == "NFTokenPage"
        elif isModifiedNode(node):
            return (
                node["ModifiedNode"]["LedgerEntryType"] == "NFTokenPage"
                and node["ModifiedNode"]["PreviousFields"]
                and "NFTokens" in node["ModifiedNode"]["PreviousFields"]
            )
        else:
            return False

    affected_nodes = [node for node in meta["AffectedNodes"] if has_nftoken_page(node)]

    def get_previous_nftokens(node: Node) -> List[NFToken]:
        nftokens: List[NFToken] = []
        if isModifiedNode(node):
            new_nftokens = node["ModifiedNode"]["PreviousFields"].get("NFTokens")
            if new_nftokens is not None:
                nftokens = cast(List[NFToken], new_nftokens)
        return nftokens

    previous_token_ids = set(
        get_nftoken_ids_from_nftokens(flatmap(get_previous_nftokens, affected_nodes))
    )

    def get_new_nftokens(
        node: Union[CreatedNode, ModifiedNode, DeletedNode]
    ) -> List[NFToken]:
        nftokens: List[NFToken] = []
        if isModifiedNode(node):
            nftokens = node["ModifiedNode"]["FinalFields"].get("NFTokens") or nftokens
        if isCreatedNode(node):
            nftokens = node["CreatedNode"]["NewFields"].get("NFTokens") or nftokens
        return nftokens

    final_token_ids = get_nftoken_ids_from_nftokens(
        flatmap(get_new_nftokens, affected_nodes)
    )

    # Get the NFTokenID which wasn't there before this transaction completed.
    return [id for id in final_token_ids if (id not in previous_token_ids)][0]
