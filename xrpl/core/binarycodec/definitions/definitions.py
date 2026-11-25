"""Maps and helpers providing serialization-related information about fields."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Generator, Optional, Union, cast

from xrpl.core.binarycodec.definitions.field_header import FieldHeader
from xrpl.core.binarycodec.definitions.field_info import FieldInfo
from xrpl.core.binarycodec.definitions.field_instance import FieldInstance
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException


def load_definitions(filename: str = "definitions.json") -> Dict[str, Any]:
    """
    Loads JSON from the definitions file and converts it to a preferred format.
    The definitions file contains information required for the XRP Ledger's
    canonical binary serialization format:
    `Serialization <https://xrpl.org/serialization.html>`_

    Args:
        filename: The name of the definitions file.
            (The definitions file should be drop-in compatible with the one from the
            ripple-binary-codec JavaScript package.)

    Returns:
        A dictionary containing the mappings provided in the definitions file.
    """
    dirname = os.path.dirname(__file__)
    absolute_path = os.path.join(dirname, filename)
    with open(absolute_path) as definitions_file:
        definitions = json.load(definitions_file)
        return _parse_definitions(definitions)


def load_definitions_from_path(path: str) -> Dict[str, Any]:
    """
    Loads JSON from an absolute file path and converts it to a preferred format.

    Args:
        path: The absolute path to the definitions file.

    Returns:
        A dictionary containing the mappings provided in the definitions file.
    """
    with open(path) as definitions_file:
        definitions = json.load(definitions_file)
        return _parse_definitions(definitions)


def _parse_definitions(definitions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses raw definitions JSON into the internal format.

    Args:
        definitions: The raw definitions dict (as loaded from JSON).

    Returns:
        A dictionary containing the mappings in the preferred format.
    """
    return {
        "TYPES": definitions["TYPES"],
        # type_name str: type_sort_key int
        "FIELDS": {
            k: v for (k, v) in definitions["FIELDS"]
        },  # convert list of tuples to dict
        # "field_name" str: {
        #   "nth": field_sort_key int,
        #   "isVLEncoded": bool,
        #   "isSerialized": bool,
        #   "isSigningField": bool,
        #   "type": string
        # }
        "LEDGER_ENTRY_TYPES": definitions.get("LEDGER_ENTRY_TYPES", {}),
        "TRANSACTION_RESULTS": definitions.get("TRANSACTION_RESULTS", {}),
        "TRANSACTION_TYPES": definitions.get("TRANSACTION_TYPES", {}),
    }


# Granular permissions that are not derived from transaction types
DEFAULT_GRANULAR_PERMISSIONS: Dict[str, int] = {
    "TrustlineAuthorize": 65537,
    "TrustlineFreeze": 65538,
    "TrustlineUnfreeze": 65539,
    "AccountDomainSet": 65540,
    "AccountEmailHashSet": 65541,
    "AccountMessageKeySet": 65542,
    "AccountTransferRateSet": 65543,
    "AccountTickSizeSet": 65544,
    "PaymentMint": 65545,
    "PaymentBurn": 65546,
    "MPTokenIssuanceLock": 65547,
    "MPTokenIssuanceUnlock": 65548,
}


class DefinitionsRegistry:
    """
    A registry that holds all definition mappings for the binary codec.

    This class encapsulates all the lookup tables needed for serialization
    and deserialization. Multiple registries can exist for different networks
    (e.g., XRPL mainnet, Xahau, sidechains).

    Example:
        >>> registry = DefinitionsRegistry.from_path("/path/to/definitions.json")
        >>> registry.get_transaction_type_code("Payment")
        0
    """

    def __init__(
        self,
        definitions: Dict[str, Any],
        granular_permissions: Optional[Dict[str, int]] = None,
    ) -> None:
        """
        Initialize a DefinitionsRegistry from a parsed definitions dict.

        Args:
            definitions: A definitions dict in the format returned by
                load_definitions().
            granular_permissions: Optional custom granular permissions. Defaults to
                DEFAULT_GRANULAR_PERMISSIONS.

        Raises:
            XRPLBinaryCodecException: If the definitions are malformed.
        """
        if granular_permissions is None:
            granular_permissions = DEFAULT_GRANULAR_PERMISSIONS

        self._definitions = definitions
        self._type_ordinal_map: Dict[str, int] = definitions["TYPES"]

        # Build reverse lookup maps
        self._transaction_type_code_to_str: Dict[int, str] = {
            value: key for key, value in definitions["TRANSACTION_TYPES"].items()
        }
        self._transaction_results_code_to_str: Dict[int, str] = {
            value: key for key, value in definitions["TRANSACTION_RESULTS"].items()
        }
        self._ledger_entry_types_code_to_str: Dict[int, str] = {
            value: key for key, value in definitions["LEDGER_ENTRY_TYPES"].items()
        }

        # Build delegable permissions (tx types + 1, plus granular)
        tx_delegations = {
            key: value + 1 for key, value in definitions["TRANSACTION_TYPES"].items()
        }
        self._delegable_permissions_str_to_code: Dict[str, int] = {
            **tx_delegations,
            **granular_permissions,
        }
        self._delegable_permissions_code_to_str: Dict[int, str] = {
            value: key for key, value in self._delegable_permissions_str_to_code.items()
        }

        # Build field maps
        self._field_info_map: Dict[str, FieldInfo] = {}
        self._field_header_name_map: Dict[FieldHeader, str] = {}

        try:
            for field in definitions["FIELDS"]:
                field_entry = definitions["FIELDS"][field]
                field_info = FieldInfo(
                    field_entry["nth"],
                    field_entry["isVLEncoded"],
                    field_entry["isSerialized"],
                    field_entry["isSigningField"],
                    field_entry["type"],
                )
                header = FieldHeader(
                    self._type_ordinal_map[field_entry["type"]], field_entry["nth"]
                )
                self._field_info_map[field] = field_info
                self._field_header_name_map[header] = field
        except KeyError as e:
            raise XRPLBinaryCodecException(
                f"Malformed definitions file. (Original exception: KeyError: {e})"
            )

    @classmethod
    def from_path(
        cls,
        path: str,
        granular_permissions: Optional[Dict[str, int]] = None,
    ) -> "DefinitionsRegistry":
        """
        Create a DefinitionsRegistry from a definitions JSON file path.

        Args:
            path: The absolute path to the definitions file.
            granular_permissions: Optional custom granular permissions.

        Returns:
            A new DefinitionsRegistry instance.
        """
        definitions = load_definitions_from_path(path)
        return cls(definitions, granular_permissions)

    @classmethod
    def default(cls) -> "DefinitionsRegistry":
        """
        Create a DefinitionsRegistry with the default XRPL definitions.

        Returns:
            A new DefinitionsRegistry instance with default definitions.
        """
        return cls(load_definitions())

    def get_field_type_name(self, field_name: str) -> str:
        """Returns the serialization data type for the given field name."""
        return self._field_info_map[field_name].type

    def get_field_type_code(self, field_name: str) -> int:
        """Returns the type code associated with the given field."""
        field_type_name = self.get_field_type_name(field_name)
        field_type_code = self._type_ordinal_map[field_type_name]
        if not isinstance(field_type_code, int):
            raise XRPLBinaryCodecException(
                "Field type codes in definitions.json must be ints."
            )
        return field_type_code

    def get_field_code(self, field_name: str) -> int:
        """Returns the field code associated with the given field."""
        return self._field_info_map[field_name].nth

    def get_field_header_from_name(self, field_name: str) -> FieldHeader:
        """Returns a FieldHeader object for a field of the given field name."""
        return FieldHeader(
            self.get_field_type_code(field_name), self.get_field_code(field_name)
        )

    def get_field_name_from_header(self, field_header: FieldHeader) -> str:
        """Returns the field name described by the given FieldHeader object."""
        return self._field_header_name_map[field_header]

    def get_field_instance(self, field_name: str) -> FieldInstance:
        """Return a FieldInstance object for the given field name."""
        info = self._field_info_map[field_name]
        field_header = self.get_field_header_from_name(field_name)
        return FieldInstance(info, field_name, field_header)

    def get_transaction_type_code(self, transaction_type: str) -> int:
        """Return an integer representing the given transaction type string."""
        return cast(int, self._definitions["TRANSACTION_TYPES"][transaction_type])

    def get_transaction_type_name(self, transaction_type: int) -> str:
        """Return string representing the given transaction type from the enum."""
        return cast(str, self._transaction_type_code_to_str[transaction_type])

    def get_transaction_result_code(self, transaction_result_type: str) -> int:
        """Return an integer representing the given transaction result string."""
        return cast(
            int, self._definitions["TRANSACTION_RESULTS"][transaction_result_type]
        )

    def get_transaction_result_name(self, transaction_result_type: int) -> str:
        """Return string representing the given transaction result type."""
        return cast(str, self._transaction_results_code_to_str[transaction_result_type])

    def get_ledger_entry_type_code(self, ledger_entry_type: str) -> int:
        """Return an integer representing the given ledger entry type string."""
        return cast(int, self._definitions["LEDGER_ENTRY_TYPES"][ledger_entry_type])

    def get_ledger_entry_type_name(self, ledger_entry_type: int) -> str:
        """Return string representing the given ledger entry type."""
        return cast(str, self._ledger_entry_types_code_to_str[ledger_entry_type])

    def get_permission_value_type_code(self, permission_value: str) -> int:
        """Return an integer representing the given permission value string."""
        return self._delegable_permissions_str_to_code[permission_value]

    def get_permission_value_type_name(self, permission_value: int) -> str:
        """Return string representing the given permission value."""
        return self._delegable_permissions_code_to_str[permission_value]


# Context variable for thread-safe registry switching
_registry_context: ContextVar[Optional[DefinitionsRegistry]] = ContextVar(
    "definitions_registry", default=None
)

# Default registry instance (lazy initialized)
_default_registry: Optional[DefinitionsRegistry] = None


def _get_default_registry() -> DefinitionsRegistry:
    """Get or create the default registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = DefinitionsRegistry.default()
    return _default_registry


def _get_current_registry() -> DefinitionsRegistry:
    """Get the current registry (from context or default)."""
    registry = _registry_context.get()
    if registry is not None:
        return registry
    return _get_default_registry()


def set_default_registry(registry: DefinitionsRegistry) -> None:
    """
    Set the global default registry.

    This affects all code not using a scoped registry via `using_definitions()`.

    Args:
        registry: The registry to use as the new default.

    Example:
        >>> custom = DefinitionsRegistry.from_path("/path/to/xahau_definitions.json")
        >>> set_default_registry(custom)
    """
    global _default_registry
    _default_registry = registry


@contextmanager
def using_definitions(
    source: Union[str, Dict[str, Any], DefinitionsRegistry],
    granular_permissions: Optional[Dict[str, int]] = None,
) -> Generator[DefinitionsRegistry, None, None]:
    """
    Context manager for using custom definitions in a scoped block.

    This is thread-safe and async-safe via contextvars.

    Args:
        source: Either a file path (str), a definitions dict, or a DefinitionsRegistry.
        granular_permissions: Optional custom granular permissions (ignored if source
            is already a DefinitionsRegistry).

    Yields:
        The DefinitionsRegistry being used.

    Example:
        >>> with using_definitions("/path/to/xahau_definitions.json") as registry:
        ...     encode(tx)  # Uses Xahau definitions
        >>> encode(tx)  # Back to default definitions
    """
    if isinstance(source, DefinitionsRegistry):
        registry = source
    elif isinstance(source, str):
        registry = DefinitionsRegistry.from_path(source, granular_permissions)
    else:
        registry = DefinitionsRegistry(source, granular_permissions)

    token = _registry_context.set(registry)
    try:
        yield registry
    finally:
        _registry_context.reset(token)


def update_definitions(
    source: Union[str, Dict[str, Any]],
    granular_permissions: Optional[Dict[str, int]] = None,
) -> None:
    """
    Update the default definitions used by the binary codec.

    This allows switching to custom definitions at runtime, e.g., for
    different networks (Xahau, sidechains) or testing.

    Args:
        source: Either a file path (str) to a definitions JSON file,
            or a pre-parsed definitions dict.
        granular_permissions: Optional custom granular permissions.

    Example:
        >>> from xrpl.core.binarycodec.definitions import definitions
        >>> definitions.update_definitions("/path/to/xahau_definitions.json")
        >>> # Now all encode/decode operations use Xahau definitions
    """
    if isinstance(source, str):
        registry = DefinitionsRegistry.from_path(source, granular_permissions)
    else:
        registry = DefinitionsRegistry(source, granular_permissions)
    set_default_registry(registry)


# =============================================================================
# Backwards-compatible module-level functions
# These delegate to the current registry (context-local or default)
# =============================================================================


def get_field_type_name(field_name: str) -> str:
    """
    Returns the serialization data type for the given field name.
    `Serialization Type List <https://xrpl.org/serialization.html#type-list>`_

    Args:
        field_name: The name of the field to get the serialization data type for.

    Returns:
        The serialization data type for the given field name.
    """
    return _get_current_registry().get_field_type_name(field_name)


def get_field_type_code(field_name: str) -> int:
    """
    Returns the type code associated with the given field.
    `Serialization Type Codes <https://xrpl.org/serialization.html#type-codes>`_

    Args:
        field_name: The name of the field get a type code for.

    Returns:
        The type code associated with the given field name.

    Raises:
        XRPLBinaryCodecException: If definitions.json is invalid.
    """
    return _get_current_registry().get_field_type_code(field_name)


def get_field_code(field_name: str) -> int:
    """
    Returns the field code associated with the given field.
    `Serialization Field Codes <https://xrpl.org/serialization.html#field-codes>`_

    Args:
        field_name: The name of the field to get a field code for.

    Returns:
        The field code associated with the given field.
    """
    return _get_current_registry().get_field_code(field_name)


def get_field_header_from_name(field_name: str) -> FieldHeader:
    """
    Returns a FieldHeader object for a field of the given field name.

    Args:
        field_name: The name of the field to get a FieldHeader for.

    Returns:
        A FieldHeader object for a field of the given field name.
    """
    return _get_current_registry().get_field_header_from_name(field_name)


def get_field_name_from_header(field_header: FieldHeader) -> str:
    """
    Returns the field name described by the given FieldHeader object.

    Args:
        field_header: The header to get a field name for.

    Returns:
        The name of the field described by the given FieldHeader.
    """
    return _get_current_registry().get_field_name_from_header(field_header)


def get_field_instance(field_name: str) -> FieldInstance:
    """
    Return a FieldInstance object for the given field name.

    Args:
        field_name: The name of the field to get a FieldInstance for.

    Returns:
        A FieldInstance object for the given field name.
    """
    return _get_current_registry().get_field_instance(field_name)


def get_transaction_type_code(transaction_type: str) -> int:
    """
    Return an integer representing the given transaction type string in an enum.

    Args:
        transaction_type: The name of the transaction type to get the enum value for.

    Returns:
        An integer representing the given transaction type string in an enum.
    """
    return _get_current_registry().get_transaction_type_code(transaction_type)


def get_transaction_type_name(transaction_type: int) -> str:
    """
    Return string representing the given transaction type from the enum.

    Args:
        transaction_type: The enum value of the transaction type.

    Returns:
        The string name of the transaction type.
    """
    return _get_current_registry().get_transaction_type_name(transaction_type)


def get_transaction_result_code(transaction_result_type: str) -> int:
    """
    Return an integer representing the given transaction result string in an enum.

    Args:
        transaction_result_type: The name of the transaction result type to get the
            enum value for.

    Returns:
        An integer representing the given transaction result type string in an enum.
    """
    return _get_current_registry().get_transaction_result_code(transaction_result_type)


def get_transaction_result_name(transaction_result_type: int) -> str:
    """
    Return string representing the given transaction result type from the enum.

    Args:
        transaction_result_type: The enum value of the transaction result type.

    Returns:
        The string name of the transaction result type.
    """
    return _get_current_registry().get_transaction_result_name(transaction_result_type)


def get_ledger_entry_type_code(ledger_entry_type: str) -> int:
    """
    Return an integer representing the given ledger entry type string in an enum.

    Args:
        ledger_entry_type: The name of the ledger entry type to get the enum value for.

    Returns:
        An integer representing the given ledger entry type string in an enum.
    """
    return _get_current_registry().get_ledger_entry_type_code(ledger_entry_type)


def get_ledger_entry_type_name(ledger_entry_type: int) -> str:
    """
    Return string representing the given ledger entry type from the enum.

    Args:
        ledger_entry_type: The enum value of the ledger entry type.

    Returns:
        The string name of the ledger entry type.
    """
    return _get_current_registry().get_ledger_entry_type_name(ledger_entry_type)


def get_permission_value_type_code(permission_value: str) -> int:
    """
    Return an integer representing the given permission value string.

    Args:
        permission_value: The name of the permission value to get the integer value for.

    Returns:
        An integer representing the given permission value string.
    """
    return _get_current_registry().get_permission_value_type_code(permission_value)


def get_permission_value_type_name(permission_value: int) -> str:
    """
    Return string representing the given permission value from the integer.

    Args:
        permission_value: The integer permission value.

    Returns:
        The string name of the permission value.
    """
    return _get_current_registry().get_permission_value_type_name(permission_value)
