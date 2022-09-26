"""The models for a transaction's metadata"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union

from xrpl.models.amounts import Amount
from xrpl.models.base_model import BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.ledger_objects.ledger_object import LedgerEntryType, LedgerObject
from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

N = TypeVar("N", bound="AffectedNode")


@require_kwargs_on_init
@dataclass(frozen=True)
class NewFields(LedgerObject):
    """A model for a node's `NewFields`"""

    pass


@require_kwargs_on_init
@dataclass(frozen=True)
class PreviousFields(LedgerObject):
    """A model for a node's `PreviousFields`"""

    pass


@require_kwargs_on_init
@dataclass(frozen=True)
class FinalFields(LedgerObject):
    """A model for a node's `FinalFields`"""

    pass


@require_kwargs_on_init
@dataclass(frozen=True)
class AffectedNode(NestedModel):
    """A model a transaction's metadata's node."""

    ledger_entry_type: LedgerEntryType = REQUIRED  # type: ignore
    ledger_index: str = REQUIRED  # type: ignore

    @classmethod
    def from_dict(cls: Type[N], value: Dict[str, Any]) -> N:
        """Derive the model from a dict.

        Args:
            value: The dictionary to derive from.

        Returns:
            N: The node type.

        Raises:
            XRPLModelException: If the provided node type does not exist.
        """
        affected_node_type = list(value.keys())[0]
        if cls.__name__ == "AffectedNode":
            if affected_node_type not in [
                "created_node",
                "modified_node",
                "deleted_node",
            ]:
                raise XRPLModelException(f"{affected_node_type} is no node type.")
            correct_type = cls.get_node_type(affected_node_type)
            return correct_type.from_dict(value)  # type: ignore
        else:
            # TODO: Check for error
            affected_node = value[affected_node_type]
            ledger_entry_type = affected_node["ledger_entry_type"]

            new_fields = affected_node.get("new_fields")
            if new_fields is not None:
                value[affected_node_type]["new_fields"][
                    "ledger_entry_type"
                ] = ledger_entry_type

            previous_fields = affected_node.get("previous_fields")
            if previous_fields is not None:
                value[affected_node_type]["previous_fields"][
                    "ledger_entry_type"
                ] = ledger_entry_type

            final_fields = affected_node.get("final_fields")
            if final_fields is not None:
                value[affected_node_type]["final_fields"][
                    "ledger_entry_type"
                ] = ledger_entry_type

            return super(AffectedNode, cls).from_dict(value)  # type: ignore

    @classmethod
    def get_node_type(cls: Type[AffectedNode], node_type: str) -> Type[AffectedNode]:
        """Get the correct model

        Args:
            node_type: The node type willing to get.

        Returns:
            Type[AffectedNode]: The correct node type

        Raises:
            XRPLModelException: If the provided node type does not exist.
        """
        if node_type == "created_node":
            return CreatedNode
        elif node_type == "modified_node":
            return ModifiedNode
        elif node_type == "deleted_node":
            return DeletedNode
        else:
            raise XRPLModelException(f"{node_type} is no node type.")

    def __getitem__(self: AffectedNode, field_name: str) -> Any:
        """Enable to get the fields like from a `dict`

        Args:
            field_name: The field's name to get the value from.

        Returns:
            Any: The value of the field.
        """
        if field_name == self.__class__.__name__ or self.__class__.__name__ == "".join(
            [word.capitalize() for word in field_name.split("_")]
        ):
            return self
        return self.__getattribute__(field_name)


@require_kwargs_on_init
@dataclass(frozen=True)
class CreatedNode(AffectedNode):
    """A model for when a new node got created on the XRPL"""

    new_fields: NewFields = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class ModifiedNode(AffectedNode):
    """A model for when a node got modified in the XRPL"""

    final_fields: FinalFields = REQUIRED  # type: ignore
    previous_fields: Optional[PreviousFields] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None


@require_kwargs_on_init
@dataclass(frozen=True)
class DeletedNode(AffectedNode):
    """A model for when a node got deleted from the XRPL"""

    final_fields: FinalFields = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class Metadata(BaseModel):
    """A model for a transaction's metadata"""

    affected_nodes: List[AffectedNode] = REQUIRED  # type: ignore
    transaction_index: int = REQUIRED  # type: ignore
    transaction_result: str = REQUIRED  # type: ignore
    delivered_amount: Optional[Union[Amount, Literal["unavailable"]]] = None

    def __getitem__(self: Metadata, field_name: str) -> Any:
        """Enable to get the fields like from a `dict`

        Args:
            field_name: The field's name to get the value from.
        """
        if field_name == self.__class__.__name__ or self.__class__.__name__ == "".join(
            [word.capitalize() for word in field_name.split("_")]
        ):
            return self
        return self.__getattribute__(field_name)
