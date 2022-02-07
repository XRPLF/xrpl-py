"""Parse order book changes caused by a transaction."""

from typing import Any, Dict, List, Union

from xrpl.utils.tx_parser.utils import (
    XRPLNoOffersAffectedException,
    filter_nodes,
    group_by_address_order,
    is_valid_metadata,
    normalize_nodes,
)


class OrderBookChanges:
    """Parse order book changes from a transactions metadata
    in a easy-to-read format.

    Args:
        metadata (`Dict[str, Union[str, int, bool, Dict[str, Any]]]`):
            The transactions metadata.
    """

    all_orderbook_changes: Dict[str, List[Dict[str, Any]]] = {}
    """All orderbook_changes"""

    def __init__(
        self: Any, metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]]
    ) -> None:
        """
        Args:
            metadata (`Dict[str, Union[str, int, bool, Dict[str, Any]]]`):
                The transactions metadata.
        """
        self.metadata = metadata

    def _define_results(self: Any, result: Dict[str, List[Dict[str, Any]]]) -> None:
        self.all_orderbook_changes = result


class ParseOrderBookChanges(OrderBookChanges):
    """Parse order book changes.

    Usage:
        Parse all orderbook changes:
            ``ParseOrderBookChanges(metadata=tx).all_orderbook_changes``

    Args:
        metadata (`Dict[str, Union[str, int, bool, Dict[str, Any]]]`):
            The transactions metadata.
    """

    def __init__(
        self: Any, metadata: Dict[str, Union[str, int, bool, Dict[str, Any]]]
    ) -> None:
        """
        Args:
            metadata (`Dict[str, Union[str, int, bool, Dict[str, Any]]]`):
                The transactions metadata.
        """
        super().__init__(metadata)

        self._parse()

    def _parse(self: Any) -> None:
        is_valid_metadata(metadata=self.metadata)
        nodes = normalize_nodes(metadata=self.metadata)

        order_changes = filter_nodes(nodes=nodes)

        if not order_changes:
            raise XRPLNoOffersAffectedException(
                "The transaction did not affected any offer."
            )

        result = group_by_address_order(order_changes)

        self._define_results(result=result)
