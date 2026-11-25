"""Handles the XRPL type and definition specifics."""

from xrpl.core.binarycodec.definitions.definitions import (
    DEFAULT_GRANULAR_PERMISSIONS,
    DefinitionsRegistry,
    get_field_header_from_name,
    get_field_instance,
    get_field_name_from_header,
    get_ledger_entry_type_code,
    get_ledger_entry_type_name,
    get_permission_value_type_code,
    get_permission_value_type_name,
    get_transaction_result_code,
    get_transaction_result_name,
    get_transaction_type_code,
    get_transaction_type_name,
    load_definitions,
    set_default_registry,
    using_definitions,
)
from xrpl.core.binarycodec.definitions.field_header import FieldHeader
from xrpl.core.binarycodec.definitions.field_info import FieldInfo
from xrpl.core.binarycodec.definitions.field_instance import FieldInstance

__all__ = [
    # Classes
    "DefinitionsRegistry",
    "FieldHeader",
    "FieldInfo",
    "FieldInstance",
    # Registry management
    "load_definitions",
    "set_default_registry",
    "using_definitions",
    "DEFAULT_GRANULAR_PERMISSIONS",
    # Field lookups
    "get_field_header_from_name",
    "get_field_name_from_header",
    "get_field_instance",
    # Type lookups
    "get_ledger_entry_type_code",
    "get_ledger_entry_type_name",
    "get_transaction_result_code",
    "get_transaction_result_name",
    "get_transaction_type_code",
    "get_transaction_type_name",
    "get_permission_value_type_code",
    "get_permission_value_type_name",
]
