from xrpl.utils.xrp_conversions import drops_to_xrp
import pydash

"""
This is a rewritten repository of https://github.com/ripple/ripple-lib-extensions/blob/master/transactionparser/src/balancechanges.js in python.
"""

### Utils ###
class Normalized_Node():
    def __init__(self, difftype: str, entryType: str, ledgerIndex: str, newFields: dict, finalFields: dict, previousFields: dict) -> None:
        self.DiffType = difftype
        self.EntryType = entryType
        self.LedgerIndex = ledgerIndex
        self.NewFields = newFields
        self.FinalFields = finalFields
        self.PreviousFields = previousFields


def __normalize_node(affectedNode):
    diffType = list(affectedNode.keys())[0]
    node = affectedNode[diffType]
    n = Normalized_Node(
        difftype=diffType,
        entryType=node["LedgerEntryType"],
        ledgerIndex=node["LedgerIndex"],
        newFields=node["NewFields"] if "NewFields" in node.keys() else {},
        finalFields=node["FinalFields"] if "FinalFields" in node.keys() else {},
        previousFields=node["PreviousFields"] if "PreviousFields" in node.keys() else {}
    )
    
    return n


def __normalize_nodes(metadata):
    affectedNodes = metadata["meta"]["AffectedNodes"]
    if not affectedNodes:
        return []

    return map(__normalize_node, affectedNodes)


class Balance():
    def __init__(self, counterparty, currency, value) -> None:
        self.Counterparty = counterparty
        self.Currency = currency
        self.Value = str(value)


class TrustLine_Quantity():
    def __init__(self, address, balance) -> None:
        self.Address = address,
        self.Balance = Balance(
            counterparty=balance["counterparty"],
            currency=balance["currency"],
            value=balance["value"]
        )
###############


def __group_by_address(balanceChanges):
    grouped = pydash.group_by(balanceChanges, lambda node: node.Address)
    
    return pydash.map_values(grouped, lambda group: pydash.map_(group, lambda node: node.Balance))


def __parse_value(value):
    if "value" in value:
        return float(value["value"])
    else:
        return float(value)


def __compute_balance_changes(node):
    value = None
    if "Balance" in node.NewFields.keys():
        value = __parse_value(node.NewFields["Balance"])
    elif "Balance" in node.PreviousFields.keys() and "Balance" in node.FinalFields.keys():
        value = __parse_value(node.FinalFields["Balance"]) - __parse_value(node.PreviousFields["Balance"])

    return None if value == None else None if value == 0 else value


def __parse_final_balance(node):
    if "Balance" in node.NewFields.keys():
        return __parse_value(node.NewFields["Balance"])
    elif "Balance" in node.FinalFields.keys():
        return __parse_value(node.FinalFields["Balance"])

    return None


def __parse_XRP_quantity(node, valueParser):
    value = valueParser(node)

    if value == None:
        return None

    isNegative = False

    if str(value).startswith("-"):
        isNegative = True
    
    result = TrustLine_Quantity(
        address=node.FinalFields["Account"] if node.FinalFields else node.NewFields["Account"],
        balance={
            "counterparty": "",
            "currency": "XRP",
            "value": drops_to_xrp(str(abs(int(value)))) if not isNegative else "-{}".format(drops_to_xrp(str(abs(int(value))))) # 'drops_to_xrp' does not accept negtive numbers
        }
    )

    return result


def __flip_TrustLine_perspective(quantity):
    negatedBalance = abs(float(quantity.Balance.Value))
    result = TrustLine_Quantity(
        address=quantity.Balance.Counterparty,
        balance={
            "counterparty": quantity.Address,
            "currency": quantity.Balance.Currency,
            "value": negatedBalance
        }
    )

    return result


def __parse_TrustLine_quantity(node, valueParser):
    value = valueParser(node)

    if value == None:
        return None

    fields = node.FinalFields if pydash.is_empty(node.NewFields) else node.NewFields

    # the balance is always from low node's perspective
    result = TrustLine_Quantity(
        address=fields["LowLimit"]["issuer"],
        balance={
            "counterparty": fields["HighLimit"]["issuer"],
            "currency": fields["Balance"]["currency"],
            "value": value 
        }
    )

    return [result, __flip_TrustLine_perspective(result)]


def __parse_quantities(metadata, valueParser):
    values = map(lambda node: __parse_XRP_quantity(node, valueParser) if node.EntryType == "AccountRoot" else __parse_TrustLine_quantity(node, valueParser) if node.EntryType == "RippleState" else [], __normalize_nodes(metadata=metadata))

    return __group_by_address(pydash.compact(pydash.flatten(values)))


def parse_balance_changes(metadata: dict) -> dict:
    """
    :param metadata: transaction metadata as dict
    :returns: parsed balance changes
    """
    parsedQuantities = __parse_quantities(metadata=metadata, valueParser=__compute_balance_changes)

    result = {}
    for k, v in parsedQuantities.items():
        address = k[0]
        change = v
        result[address] = []
        for obj in change:
            if type(obj.Counterparty) == tuple:
                obj.Counterparty = obj.Counterparty[0]
            result[address].append({
                "Counterparty": obj.Counterparty,
                "Currency": obj.Currency,
                "Value": obj.Value
            })

    return result


def parse_final_balances(metadata):
    parsedQuantities = __parse_quantities(metadata, __parse_final_balance)

    result = {}
    for k, v in parsedQuantities.items():
        address = k[0]
        change = v
        result[address] = []
        for obj in change:
            if type(obj.Counterparty) == tuple:
                obj.Counterparty = obj.Counterparty[0]
            result[address].append({
                "Counterparty": obj.Counterparty,
                "Currency": obj.Currency,
                "Value": obj.Value
            })

    return result
