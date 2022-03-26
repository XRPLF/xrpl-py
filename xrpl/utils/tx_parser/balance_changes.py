"""
Parse balance changes, final balances and previous balances of every
account involved in the given transaction.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from xrpl.utils.tx_parser.utils import (
    compute_balance_changes,
    is_valid_metadata,
    normalize_metadata,
    normalize_nodes,
    parse_final_balance,
    parse_quantities,
)


class BalanceChanges:
    """Parse balance changes from a transactions metadata
    in a easy-to-read format.
    """

    all_balances: Dict[str, List[Dict[str, str]]] = {}
    """All balance changes of all accounts
    affected by the transaction.
    """
    source_account_balances: Dict[str, List[Dict[str, str]]] = {}
    """All balance changes of the source account (Field: `Account`)
    which was affected by the transaction.
    """
    destination_account_balances: Optional[Dict[str, List[Dict[str, str]]]] = None
    """All balance changes of the destination account (Field: `Destination`)
    which was affected by the transaction if field is included in metadata.
    """

    def __init__(self: BalanceChanges, metadata: Any) -> None:
        """
        Attributes:
            metadata:
                Transaction metadata including the account that
                sent the transaction and the affected nodes.
        """
        self.metadata = metadata

    def _define_results(
        self: BalanceChanges,
        result: Dict[str, List[Dict[str, str]]],
    ) -> None:
        self.all_balances = result
        source_account = str(self.metadata["Account"])
        self.source_account_balances = {
            source_account: self.all_balances[source_account]
        }
        try:
            destination_account = str(self.metadata["Destination"])
            self.destination_account_balances = {
                destination_account: self.all_balances[destination_account]
            }
        except KeyError:
            self.destination_account_balances = None


class ParseBalanceChanges(BalanceChanges):
    """Parse the balance changes of all accounts affected
    by the transaction after it occurred.
    """

    def __init__(
        self: ParseBalanceChanges,
        metadata: Dict[  # metadata received from a tx method
            str,
            Union[
                str,
                int,
                Dict[  # issued currency amount
                    str,
                    str,
                ],
                List[  # Field: 'paths'
                    List[
                        Dict[
                            str,
                            Union[
                                str,
                                int,
                            ],
                        ],
                    ],
                ],
                Dict[  # Field: 'meta'
                    str,  # 'AffectedNodes'
                    List[
                        Dict[
                            str,  # Node state
                            Dict[
                                str,
                                Union[
                                    str,
                                    int,
                                    Dict[str, Union[str, int, Dict[str, str]]],
                                ],
                            ],
                        ],
                    ],
                ],
            ],
        ],
    ) -> None:
        """
        Attributes:
            metadata:
                Transaction metadata including the account that
                sent the transaction and the affected nodes.

        Usage:
            Parse all balance changes:
                `ParseBalanceChanges(metadata=tx).all_balances`
            Parse balance changes of the account that sent the transaction:
                `ParseBalanceChanges(metadata=tx).source_account_balances`
            Parse balance changes of the account that received the transaction:
                `ParseBalanceChanges(metadata=tx).destination_account_balances`
                    If provided transaction has no field `Destination`:
                        `None`
        """
        super().__init__(metadata)

        self._parse()

    def _parse(self: ParseBalanceChanges) -> None:
        is_valid_metadata(metadata=self.metadata)
        if "transaction" in self.metadata:
            self.metadata = normalize_metadata(self.metadata)

        nodes = normalize_nodes(metadata=self.metadata)
        parsedQuantities = parse_quantities(
            nodes=nodes, value_parser=compute_balance_changes
        )

        result: Dict[str, List[Dict[str, str]]] = {}
        for address, change in parsedQuantities.items():
            result[address] = []
            for obj in change:
                if isinstance(obj.counterparty, tuple):
                    obj.counterparty = obj.counterparty[0]
                result[address].append(
                    {
                        "Counterparty": obj.counterparty,
                        "Currency": obj.currency,
                        "Value": obj.value,
                    }
                )

        self._define_results(result=result)


class ParseFinalBalances(BalanceChanges):
    """Parse the final balances of all accounts affected
    by the transaction after it occurred.
    """

    def __init__(
        self: ParseFinalBalances,
        metadata: Dict[  # metadata received from a tx method
            str,
            Union[
                str,
                int,
                Dict[  # issued currency amount
                    str,
                    str,
                ],
                List[  # Field: 'paths'
                    List[
                        Dict[
                            str,
                            Union[
                                str,
                                int,
                            ],
                        ],
                    ],
                ],
                Dict[  # Field: 'meta'
                    str,  # 'AffectedNodes'
                    List[
                        Dict[
                            str,  # Node state
                            Dict[
                                str,
                                Union[
                                    str,
                                    int,
                                    Dict[str, Union[str, int, Dict[str, str]]],
                                ],
                            ],
                        ],
                    ],
                ],
            ],
        ],
    ) -> None:
        """
        Attributes:
            metadata:
                Transaction metadata including the account that
                sent the transaction and the affected nodes.

        Usage:
            Parse all final balances:
                `ParseFinalBalances(metadata=tx).all_balances`
            Parse final balances of the account that sent the transaction:
                `ParseFinalBalances(metadata=tx).source_account_balances`
            Parse final balances of the account that received the transaction
                `ParseFinalBalances(metadata=tx).destination_account_balances``
                    If provided transaction has no field `Destination`:
                        `None`
        """
        super().__init__(metadata)

        self._parse()

    def _parse(self: ParseFinalBalances) -> None:
        is_valid_metadata(metadata=self.metadata)
        if "transaction" in self.metadata:
            self.metadata = normalize_metadata(self.metadata)

        nodes = normalize_nodes(metadata=self.metadata)
        parsed_quantities = parse_quantities(
            nodes=nodes,
            value_parser=parse_final_balance,
        )

        result: Dict[str, List[Dict[str, str]]] = {}
        for address, change in parsed_quantities.items():
            result[address] = []
            for obj in change:
                if isinstance(obj.counterparty, tuple):
                    obj.counterparty = obj.counterparty[0]
                result[address].append(
                    {
                        "Counterparty": obj.counterparty,
                        "Currency": obj.currency,
                        "Value": obj.value,
                    }
                )

        self._define_results(result=result)


class ParsePreviousBalances(BalanceChanges):
    """Parse the previous balances of all accounts affected
    by the transaction before it occurred.
    """

    def __init__(
        self: ParsePreviousBalances,
        metadata: Dict[  # metadata received from a tx method
            str,
            Union[
                str,
                int,
                Dict[  # issued currency amount
                    str,
                    str,
                ],
                List[  # Field: 'paths'
                    List[
                        Dict[
                            str,
                            Union[
                                str,
                                int,
                            ],
                        ],
                    ],
                ],
                Dict[  # Field: 'meta'
                    str,  # 'AffectedNodes'
                    List[
                        Dict[
                            str,  # Node state
                            Dict[
                                str,
                                Union[
                                    str,
                                    int,
                                    Dict[str, Union[str, int, Dict[str, str]]],
                                ],
                            ],
                        ],
                    ],
                ],
            ],
        ],
    ) -> None:
        """
        Attributes:
            metadata:
                Transaction metadata including the account that
                sent the transaction and the affected nodes.

        Usage:
            Parse all previous balances:
                `ParsePreviousBalances(metadata=tx).all_balances`
            Parse previous balances of the account that sent the transaction:
                `ParsePreviousBalances(metadata=tx).source_account_balances`
            Parse previous balances of the account that received the transaction:
                `ParsePreviousBalances(metadata=tx).destination_account_balances`
                    `None`
        """
        super().__init__(metadata)

        self._parse()

    def _parse(self: ParsePreviousBalances) -> None:
        is_valid_metadata(metadata=self.metadata)
        if "transaction" in self.metadata:
            self.metadata = normalize_metadata(self.metadata)

        balance_changes = ParseBalanceChanges(metadata=self.metadata).all_balances
        final_balances = ParseFinalBalances(metadata=self.metadata).all_balances

        for account, balances in balance_changes.items():
            for count, balance in enumerate(balances):
                final_balances_value = final_balances[account][count]["Value"]
                final_balances[account][count]["Value"] = str(
                    Decimal(final_balances_value) - Decimal(balance["Value"])
                )

        self._define_results(result=final_balances)
