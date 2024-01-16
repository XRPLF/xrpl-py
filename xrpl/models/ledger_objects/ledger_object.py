"""A model for Ledger Objects"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from xrpl.models.base_model import BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType

# TODO: REMOVE if optional is needed
# from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

L = TypeVar("L", bound="LedgerObject")


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerObject(BaseModel):
    """The base model for a Ledger Object."""

    # TODO: Try without optional
    ledger_entry_type: LedgerEntryType = None
    index: Optional[str] = None

    @classmethod
    def from_dict(cls: Type[L], value: Dict[str, Any]) -> L:
        """Derive the model from a dict.

        Args:
            value: The dictionary to derive from.

        Returns:
            L: The Ledger Object.

        Raises:
            XRPLModelException: If there is no Ledger Object type is
                provided or the type mismatches the constructor type.
        """
        if cls.__name__ == "LedgerObject":
            if "ledger_entry_type" not in value:
                raise XRPLModelException(
                    "Ledger Object does not include ledger_entry_type."
                )
            correct_type = cls.get_ledger_object_type(value["ledger_entry_type"])
            return correct_type.from_dict(value)  # type: ignore
        elif cls.__name__ in ["FinalFields", "PreviousFields", "NewFields"]:
            if "ledger_entry_type" not in value:
                raise XRPLModelException(
                    "Ledger Object does not include ledger_entry_type."
                )
            correct_type = cls.get_md_ledger_object_type(value["ledger_entry_type"])
            del value["ledger_entry_type"]
            return correct_type.from_dict(value)  # type: ignore
        else:
            if "ledger_entry_type" in value:
                ledger_entry_type = value["ledger_entry_type"]
                if (
                    cls.get_ledger_object_type(ledger_entry_type).__name__
                    != cls.__name__
                    and cls.get_md_ledger_object_type(ledger_entry_type).__name__
                    != cls.__name__
                ):
                    raise XRPLModelException(
                        f"Using wrong constructor: using {cls.__name__} constructor "
                        f"with ledger object type {value['ledger_entry_type']}."
                    )
                value = {**value}
                del value["ledger_entry_type"]
            return super(LedgerObject, cls).from_dict(value)

    @classmethod
    def get_ledger_object_type(
        cls: Type[LedgerObject], ledger_object_type: str
    ) -> Type[LedgerObject]:
        """Get the correct model

        Args:
            ledger_object_type: The ledger object type willing to get.

        Returns:
            Type[AffectedNode]: The correct ledger object type.

        Raises:
            XRPLModelException: If the Ledger Object type does not exist.
        """
        import xrpl.models.ledger_objects as ledger_object_models

        ledger_object_types: Dict[str, Type[LedgerObject]] = {
            lgr_obj.value: getattr(ledger_object_models, lgr_obj)
            for lgr_obj in ledger_object_models.ledger_entry_type.LedgerEntryType
        }
        if ledger_object_type in ledger_object_types:
            return ledger_object_types[ledger_object_type]

        raise XRPLModelException(
            f"{ledger_object_type} is not a valid Ledger Object type."
        )

    @classmethod
    def get_md_ledger_object_type(
        cls: Type[LedgerObject], ledger_object_type: str
    ) -> Type[LedgerObject]:
        """
        Get the correct model

        Args:
            ledger_object_type: The object type willing to get.

        Returns:
            Type[LedgerObject]: The correct ledger object type.

        Raises:
            XRPLModelException: If the Ledger Object type does not exist.
        """
        import xrpl.models.ledger_objects as ledger_object_models

        ledger_object_types: Dict[str, Type[LedgerObject]] = {
            lgr_obj.value: getattr(ledger_object_models, f"MD{lgr_obj}Fields")
            for lgr_obj in ledger_object_models.ledger_entry_type.LedgerEntryType
        }
        if ledger_object_type in ledger_object_types:
            return ledger_object_types[ledger_object_type]

        raise XRPLModelException(
            f"{ledger_object_type} is not a valid Ledger Object type."
        )

    def __getitem__(self: LedgerObject, field_name: str) -> Any:
        """Enable to get the fields like from a `dict`"""
        if field_name == self.__class__.__name__ or self.__class__.__name__ == "".join(
            [word.capitalize() for word in field_name.split("_")]
        ):
            return self
        return self.__getattribute__(field_name)
