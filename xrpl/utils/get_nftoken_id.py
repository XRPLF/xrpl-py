"""Utils to get an NFTokenID from metadata"""
from typing import TypedDict, Union, List, cast
from typing_extensions import TypeGuard, TypeAlias
from xrpl.models.transactions.metadata import (
    CreatedNode,
    CreatedNodeFields,
    DeletedNode,
    DeletedNodeFields,
    Fields,
    ModifiedNode,
    ModifiedNodeFields,
    TransactionMetadata,
)
from xrpl.models.ledger.nft import NFToken

# TODO: Add dynamic typing on the return type
def flatmap(func, objects):
    '''
    Flattens objects into a single list, and applies func to every object in objects. 

    Source: https://dev.to/turbaszek/flat-map-in-python-3g98

    Args:
        func: A function to apply to every object.
        objects: A list of lists to be flattened and updated.
    '''
    return [updated_object for object in objects for updated_object in func(object)]

Node: TypeAlias = Union[CreatedNode, ModifiedNode, DeletedNode]

def isCreatedNode(node: Node) -> TypeGuard[CreatedNode]:
    return "CreatedNode" in node

def isModifiedNode(node: Node) -> TypeGuard[ModifiedNode]:
    return "ModifiedNode" in node

def isDeletedNode(node: Node) -> TypeGuard[DeletedNode]:
    return "DeletedNode" in node

def get_nftoken_id(meta: TransactionMetadata) -> str:
    '''
    Gets the NFTokenID for an NFT recently minted with NFTokenMint.

    Args:
        meta - Metadata from the response to submitting an NFTokenMint transaction.
    '''
    if meta["AffectedNodes"] == None:
        raise TypeError(f"""Unable to parse the parameter given to getNFTokenID. 
            'meta' must be the metadata from an NFTokenMint transaction. Received {meta} instead.""")

    ''' 
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
    '''


    '''
    const affectedNodes = meta.AffectedNodes.filter((node) => {
        if (isCreatedNode(node)) {
        return node.CreatedNode.LedgerEntryType === 'NFTokenPage'
        }
        if (isModifiedNode(node)) {
        return (
            node.ModifiedNode.LedgerEntryType === 'NFTokenPage' &&
            Boolean(node.ModifiedNode.PreviousFields?.NFTokens)
        )
        }
        return false
    })'''
    def has_nftoken_page(node: Union[CreatedNode, ModifiedNode, DeletedNode]):
        if(isCreatedNode(node)):
            return (node["CreatedNode"]["LedgerEntryType"] == "NFTokenPage")
        elif(isModifiedNode(node)):
            return (node["ModifiedNode"]["LedgerEntryType"] == "NFTokenPage" 
                and node["ModifiedNode"]["PreviousFields"] 
                and "NFTokens" in node["ModifiedNode"]["PreviousFields"])
        else:
            return False


    affected_nodes = filter(has_nftoken_page, meta["AffectedNodes"])

    '''
    const previousTokenIDSet = new Set(
        flatMap(affectedNodes, (node) => {
        const nftokens = isModifiedNode(node)
            ? (node.ModifiedNode.PreviousFields?.NFTokens as NFToken[])
            : []
        return nftokens.map((token) => token.NFToken.NFTokenID)
        }).filter((id) => Boolean(id)),
    )
    #TODO: Verify that the above code is mirrored below.
    '''

    def get_new_nftoken_ids(node: Node) -> List[str]:
        nftokens: List[NFToken] = []
        if(isModifiedNode(node)):
            new_nftokens = node["ModifiedNode"]["PreviousFields"].get("NFTokens")
            if(new_nftokens != None):
                nftokens = cast(List[NFToken], new_nftokens)
        return [token["NFToken"]["NFTokenId"] for token in nftokens]

    previous_token_ids = filter(lambda id : id is not None, set(flatmap(get_new_nftoken_ids, affected_nodes)))
    


    return ""
    

'''
/**
 * Gets the NFTokenID for an NFT recently minted with NFTokenMint.
 *
 * @param meta - Metadata from the response to submitting an NFTokenMint transaction.
 * @returns The NFTokenID for the minted NFT.
 * @throws if meta is not TransactionMetadata.
 */
export default function getNFTokenID(
  meta: TransactionMetadata,
): string | undefined {
  /* eslint-disable @typescript-eslint/consistent-type-assertions -- Necessary for parsing metadata */
  const previousTokenIDSet = new Set(
    flatMap(affectedNodes, (node) => {
      const nftokens = isModifiedNode(node)
        ? (node.ModifiedNode.PreviousFields?.NFTokens as NFToken[])
        : []
      return nftokens.map((token) => token.NFToken.NFTokenID)
    }).filter((id) => Boolean(id)),
  )

  /* eslint-disable @typescript-eslint/no-unnecessary-condition -- Cleaner to read */
  const finalTokenIDs = flatMap(affectedNodes, (node) =>
    (
      (((node as ModifiedNode).ModifiedNode?.FinalFields?.NFTokens ??
        (node as CreatedNode).CreatedNode?.NewFields?.NFTokens) as NFToken[]) ??
      []
    ).map((token) => token.NFToken.NFTokenID),
  ).filter((nftokenID) => Boolean(nftokenID))
  /* eslint-enable @typescript-eslint/consistent-type-assertions -- Necessary for parsing metadata */
  /* eslint-enable @typescript-eslint/no-unnecessary-condition -- Cleaner to read */

  const nftokenID = finalTokenIDs.find((id) => !previousTokenIDSet.has(id))

  return nftokenID
}
'''