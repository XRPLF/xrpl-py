"""Parse order book changes caused by a transaction."""
from __future__ import annotations

from typing import Any, Dict, List, Union

from xrpl.utils.tx_parser.utils import (
    group_by_address_order_book,
    is_valid_metadata,
    normalize_metadata,
    normalize_nodes,
    parse_order_book_changes,
)


class OrderBookChanges:
    """Parse order book changes from a transactions metadata
    in a easy-to-read format.
    """

    # all_orderbook_changes = {'account': ['order book changes']}
    all_orderbook_changes: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self: OrderBookChanges, metadata: Any) -> None:
        """
        Args:
            metadata:
                The transactions metadata.
        """
        self.metadata = metadata

    def _define_results(
        self: OrderBookChanges,
        result: Dict[
            str,
            List[
                Dict[str, Union[Dict[str, Union[Dict[str, str], str]], str, int, bool]],
            ],
        ],
    ) -> None:
        self.all_orderbook_changes = result


class ParseOrderBookChanges(OrderBookChanges):
    """Parse order book changes."""

    def __init__(
        self: ParseOrderBookChanges,
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
                The transactions metadata.

        Usage:
            Parse all orderbook changes:
                `ParseOrderBookChanges(metadata=tx).all_orderbook_changes`
        """
        super().__init__(metadata)

        self._parse()

    def _parse(self: ParseOrderBookChanges) -> None:
        is_valid_metadata(metadata=self.metadata)
        if "transaction" in self.metadata:
            self.metadata = normalize_metadata(self.metadata)

        nodes = normalize_nodes(metadata=self.metadata)
        order_changes = parse_order_book_changes(nodes=nodes)

        if order_changes:
            result = group_by_address_order_book(order_changes)
        else:
            result = {}

        self._define_results(result=result)
