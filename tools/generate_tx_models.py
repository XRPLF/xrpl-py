"""Script to generate transaction models from rippled source code."""

import os
import re
import sys
from typing import Dict, List, Tuple

from xrpl.models.base_model import _key_to_json
from xrpl.models.transactions.types.pseudo_transaction_type import PseudoTransactionType
from xrpl.models.transactions.types.transaction_type import TransactionType


def _read_file(filename: str) -> str:
    with open(filename) as f:
        return f.read()


def _format_tx_format(raw_tx_format: str) -> List[Tuple[str, ...]]:
    return [
        tuple(element.strip(" \n,{}").split(", "))
        for element in raw_tx_format.strip().split("\n")
    ]


def _parse_rippled_source(
    folder: str,
) -> Tuple[Dict[str, List[str]], Dict[str, List[Tuple[str, ...]]]]:
    # Get SFields
    sfield_cpp = _read_file(os.path.join(folder, "src/ripple/protocol/impl/SField.cpp"))
    sfield_hits = re.findall(
        r'^ *CONSTRUCT_[^\_]+_SFIELD *\( *[^,\n]*,[ \n]*"([^\"\n ]+)"[ \n]*,[ \n]*'
        + r"([^, \n]+)[ \n]*,[ \n]*([0-9]+)(,.*?(notSigning))?",
        sfield_cpp,
        re.MULTILINE,
    )
    sfields = {hit[0]: hit[1:] for hit in sfield_hits}

    # Get TxFormats
    tx_formats_cpp = _read_file(
        os.path.join(folder, "src/ripple/protocol/impl/TxFormats.cpp")
    )
    tx_formats_hits = re.findall(
        r"^ *add\(jss::([^\"\n, ]+),[ \n]*tt[A-Z_]+,[ \n]*{[ \n]*(({sf[A-Za-z0-9]+, "
        + r"soe(OPTIONAL|REQUIRED|DEFAULT)},[ \n]+)*)},[ \n]*[pseudocC]+ommonFields\);",
        tx_formats_cpp,
        re.MULTILINE,
    )
    tx_formats = {hit[0]: _format_tx_format(hit[1]) for hit in tx_formats_hits}

    return sfields, tx_formats


TYPE_MAP = {
    "UINT8": "int",
    "UINT16": "int",
    "UINT32": "int",
    "UINT64": "Union[int, str]",
    "UINT128": "str",
    "UINT160": "str",
    "UINT256": "str",
    "AMOUNT": "Amount",
    "VL": "str",
    "ACCOUNT": "str",
    "VECTOR256": "List[str]",
    "PATHSET": "List[Path]",
    "ISSUE": "Currency",
    "XCHAIN_BRIDGE": "XChainBridge",
    "OBJECT": "????",  # TODO: add inner object format support
    "ARRAY": "List[????]",
}

IMPORT_MAP = {
    "Amount": "from xrpl.models.amounts import Amount",
    "Currency": "from xrpl.models.currencies import Currency",
    "Path": "from xrpl.models.path import Path",
    "XChainBridge": "from xrpl.models.xchain_bridge import XChainBridge",
    "REQUIRED": "from xrpl.models.required import REQUIRED",
}


def _update_index_file(tx: str, name: str) -> None:
    filename = "xrpl/models/transactions/__init__.py"
    with open(filename) as f:
        index_file = f.read()
    index_file = index_file.replace(
        "    XChainModifyBridgeFlagInterface,\n)",
        "    XChainModifyBridgeFlagInterface,\n)\n"
        + f"from xrpl.models.transactions.{name} import {tx}",
    )
    index_file = index_file.replace(
        '"XChainModifyBridgeFlagInterface",',
        f'"XChainModifyBridgeFlagInterface",\n    "{tx}",',
    )
    with open(filename, "w") as f:
        f.write(index_file)


def _main(
    sfields: Dict[str, List[str]], tx_formats: Dict[str, List[Tuple[str, ...]]]
) -> None:
    txs_to_add = []
    existing_library_txs = {m.value for m in TransactionType} | {
        m.value for m in PseudoTransactionType
    }
    for tx in tx_formats:
        if tx not in existing_library_txs:
            txs_to_add.append((tx, _key_to_json(tx)))

    with open("xrpl/models/transactions/types/transaction_type.py", "a") as f:
        for tx, name in txs_to_add:
            f.write(f'    {name.upper()} = "{tx}"\n')

    for tx, name in txs_to_add:
        tx_format = tx_formats[tx]

        def _generate_param_line(param: str, is_required: bool) -> str:
            param_name = param[2:]
            param_type = sfields[param_name][0]
            if is_required:
                param_type_output = f"{TYPE_MAP[param_type]} = REQUIRED  # type: ignore"
            else:
                param_type_output = f"Optional[{TYPE_MAP[param_type]}] = None"
            return f"    {_key_to_json(param_name)}: {param_type_output}"

        param_lines = [
            _generate_param_line(param[0], param[1] == "soeREQUIRED")
            for param in sorted(tx_format, key=lambda x: x[0])
            if param != ("",)
        ]
        param_lines.sort(key=lambda x: "REQUIRED" not in x)
        params = "\n".join(param_lines)
        model = f"""@require_kwargs_on_init
@dataclass(frozen=True,  **KW_ONLY_DATACLASS)
class {tx}(Transaction):
    \"\"\"Represents a {tx} transaction.\"\"\"

{params}

    transaction_type: TransactionType = field(
        default=TransactionType.{name.upper()},
        init=False,
    )
"""

        type_imports = []
        for item in ("List", "Optional", "Union"):
            if item in model:
                type_imports.append(item)

        type_line = (
            "from typing import " + ", ".join(sorted(type_imports))
            if len(type_imports) > 0
            else ""
        )
        other_imports = []
        for item in IMPORT_MAP:
            if item in model:
                other_imports.append(IMPORT_MAP[item])
        other_import_lines = "\n".join(other_imports)

        imported_models = f"""\"\"\"Model for {tx} transaction type.\"\"\"

from __future__ import annotations

from dataclasses import dataclass, field
{type_line}

{other_import_lines}
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init, KW_ONLY_DATACLASS
"""

        imported_models = imported_models.replace("\n\n\n\n", "\n\n")
        imported_models = imported_models.replace("\n\n\n", "\n\n")
        model = model.replace("\n\n\n\n", "\n\n")

        with open(f"xrpl/models/transactions/{name}.py", "w+") as f:
            f.write(imported_models + "\n\n" + model)

        _update_index_file(tx, name)

        print("Added " + tx)


if __name__ == "__main__":
    folder = sys.argv[1]
    sfields, tx_formats = _parse_rippled_source(folder)
    _main(sfields, tx_formats)
