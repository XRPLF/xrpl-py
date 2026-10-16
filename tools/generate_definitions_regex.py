"""Script to generate the definitions.json file from rippled source code."""

import json
import os
import re
import sys
from pathlib import Path

import httpx

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("Usage: python " + sys.argv[0] + " path/to/rippled [path/to/output/file]")
    print(
        "Usage: python "
        + sys.argv[0]
        + " github.com/user/rippled/tree/feature-branch [path/to/output/file]"
    )
    sys.exit(1)

########################################################################
#  Get all necessary files from rippled
########################################################################


def _read_file_from_github(repo: str, filename: str) -> str:
    if "tree" not in repo:
        repo += "/tree/HEAD"
    url = repo.replace("github.com", "raw.githubusercontent.com")
    url = url.replace("tree/", "")
    url += "/" + filename
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        print(f"Error reading {url}: {e}", file=sys.stderr)
        sys.exit(1)


def _read_file(folder: str, filename: str) -> str:
    file_path = Path(folder) / filename
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_text()


func = _read_file_from_github if "github.com" in sys.argv[1] else _read_file

sfield_h = func(sys.argv[1], "include/xrpl/protocol/SField.h")
sfield_macro_file = func(sys.argv[1], "include/xrpl/protocol/detail/sfields.macro")
ledger_entries_file = func(
    sys.argv[1], "include/xrpl/protocol/detail/ledger_entries.macro"
)
ter_h = func(sys.argv[1], "include/xrpl/protocol/TER.h")
transactions_file = func(sys.argv[1], "include/xrpl/protocol/detail/transactions.macro")
tx_flags_h = func(sys.argv[1], "include/xrpl/protocol/TxFlags.h")
ledger_formats_h = func(sys.argv[1], "include/xrpl/protocol/LedgerFormats.h")
tx_formats_cpp = func(sys.argv[1], "src/libxrpl/protocol/TxFormats.cpp")
ledger_formats_cpp = func(sys.argv[1], "src/libxrpl/protocol/LedgerFormats.cpp")


# Translate from rippled string format to what the binary codecs expect
def _translate(inp: str) -> str:
    if re.match(r"^UINT", inp):
        if re.search(r"256|160|128|192|384|512", inp):
            return inp.replace("UINT", "Hash")
        else:
            return inp.replace("UINT", "UInt")

    non_standard_renames = {
        "OBJECT": "STObject",
        "ARRAY": "STArray",
        "ACCOUNT": "AccountID",
        "LEDGERENTRY": "LedgerEntry",
        "NOTPRESENT": "NotPresent",
        "PATHSET": "PathSet",
        "VL": "Blob",
        "DIR_NODE": "DirectoryNode",
        "PAYCHAN": "PayChannel",
        "XCHAIN_BRIDGE": "XChainBridge",
    }
    if inp in non_standard_renames:
        return non_standard_renames[inp]

    parts = inp.split("_")
    result = ""
    for part in parts:
        result += part[0:1].upper() + part[1:].lower()
    return result


output = ""


# add a new line of content to the output
def _add_line(line: str) -> None:
    global output
    output += line + "\n"


# start
_add_line("{")

########################################################################
#  SField processing
########################################################################
_add_line('  "FIELDS": [')

# The ones that are harder to parse directly from SField.cpp
_add_line("""    [
      "Generic",
      {
        "isSerialized": true,
        "isSigningField": true,
        "isVLEncoded": false,
        "nth": 0,
        "type": "Unknown"
      }
    ],
    [
      "Invalid",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": -1,
        "type": "Unknown"
      }
    ],
    [
      "ObjectEndMarker",
      {
        "isSerialized": true,
        "isSigningField": true,
        "isVLEncoded": false,
        "nth": 1,
        "type": "STObject"
      }
    ],
    [
      "ArrayEndMarker",
      {
        "isSerialized": true,
        "isSigningField": true,
        "isVLEncoded": false,
        "nth": 1,
        "type": "STArray"
      }
    ],
    [
      "taker_gets_funded",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": 258,
        "type": "Amount"
      }
    ],
    [
      "taker_pays_funded",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": 259,
        "type": "Amount"
      }
    ],""")

# Parse STypes
# Example line:
# STYPE(STI_UINT32, 2)    \
type_hits = re.findall(
    r"^ *STYPE\(STI_([^ ]*?)[ \n]*,[ \n]*([0-9-]+)[ \n]*\)[ \n]*\\?$",
    sfield_h,
    re.MULTILINE,
)
# name-to-value map - needed for SField processing
type_map = {x[0]: x[1] for x in type_hits}


def _is_vl_encoded(t: str) -> str:
    if t == "VL" or t == "ACCOUNT" or t == "VECTOR256":
        return "true"
    return "false"


def _is_serialized(t: str, name: str) -> str:
    if t == "LEDGERENTRY" or t == "TRANSACTION" or t == "VALIDATION" or t == "METADATA":
        return "false"
    if name == "hash" or name == "index":
        return "false"
    return "true"


def _is_signing_field(t: str, not_signing_field: str) -> str:
    if not_signing_field == "kNotSigning":
        return "false"
    if t == "LEDGERENTRY" or t == "TRANSACTION" or t == "VALIDATION" or t == "METADATA":
        return "false"
    return "true"


# Parse SField.cpp for all the SFields and their serialization info
# Example lines:
# TYPED_SFIELD(sfFee, AMOUNT, 8)
# UNTYPED_SFIELD(sfSigners,  ARRAY, 3, SField::sMD_Default, SField::kNotSigning)
sfield_hits = re.findall(
    r"^ *[A-Z]*TYPED_SFIELD[ \n]*\([ \n]*sf([^,\n]*),[ \n]*([^, \n]+)[ \n]*,[ \n]*"
    r"([0-9]+)(,.*?(kNotSigning))?",
    sfield_macro_file,
    re.MULTILINE,
)
sfield_hits += [
    ("hash", "UINT256", "257", "", "kNotSigning"),
    ("index", "UINT256", "258", "", "kNotSigning"),
]
sfield_hits.sort(key=lambda x: int(type_map[x[1]]) * 2**16 + int(x[2]))
for x in range(len(sfield_hits)):
    _add_line("    [")
    _add_line('      "' + sfield_hits[x][0] + '",')
    _add_line("      {")
    _add_line(
        '        "isSerialized": '
        + _is_serialized(sfield_hits[x][1], sfield_hits[x][0])
        + ","
    )
    _add_line(
        '        "isSigningField": '
        + _is_signing_field(sfield_hits[x][1], sfield_hits[x][4])
        + ","
    )
    _add_line('        "isVLEncoded": ' + _is_vl_encoded(sfield_hits[x][1]) + ",")
    _add_line('        "nth": ' + sfield_hits[x][2] + ",")
    _add_line('        "type": "' + _translate(sfield_hits[x][1]) + '"')
    _add_line("      }")
    _add_line("    ]" + ("," if x < len(sfield_hits) - 1 else ""))

_add_line("  ],")

########################################################################
#  Ledger entry type processing
########################################################################
_add_line('  "LEDGER_ENTRY_TYPES": {')


def _unhex(x: str) -> str:
    if x[0:2] == "0x":
        return str(int(x, 16))
    return x


# Parse ledger entries
# Example line:
# LEDGER_ENTRY(ltNFTOKEN_OFFER, 0x0037, NFTokenOffer, nft_offer, ({
lt_hits = re.findall(
    r"^ *LEDGER_ENTRY[A-Z_]*\(lt[A-Z_]+[ \n]*,[ \n]*([xX0-9a-fA-F]+)[ \n]*,[ \n]*"
    r"([^,]+),[ \n]*([^,]+), "
    r"\({$",
    ledger_entries_file,
    re.MULTILINE,
)
lt_hits.append(("-1", "Invalid"))
lt_hits.sort(key=lambda x: x[1])
for x in range(len(lt_hits)):
    _add_line(
        '    "'
        + lt_hits[x][1]
        + '": '
        + _unhex(lt_hits[x][0])
        + ("," if x < len(lt_hits) - 1 else "")
    )
_add_line("  },")

########################################################################
#  TER code processing
########################################################################
_add_line('  "TRANSACTION_RESULTS": {')
ter_h = str(ter_h).replace("[[maybe_unused]]", "")

# Parse TER codes
ter_code_hits = re.findall(
    r"^ *((tel|tem|tef|ter|tes|tec)[A-Z_]+)([ \n]*=[ \n]*([0-9-]+))?[ \n]*,?[ \n]*"
    r"(\/\/[^\n]*)?$",
    ter_h,
    re.MULTILINE,
)
ter_codes = []
upto = -1

# Get the exact values of the TER codes and sort them
for x in range(len(ter_code_hits)):
    if ter_code_hits[x][3] != "":
        upto = int(ter_code_hits[x][3])
    ter_codes.append((ter_code_hits[x][0], upto))

    upto += 1
ter_codes.sort(key=lambda x: x[0])

current_type = ""
for x in range(len(ter_codes)):
    # print newline between the different code types
    if current_type == "":
        current_type = ter_codes[x][0][:3]
    elif current_type != ter_codes[x][0][:3]:
        _add_line("")
        current_type = ter_codes[x][0][:3]

    _add_line(
        '    "'
        + ter_codes[x][0]
        + '": '
        + str(ter_codes[x][1])
        + ("," if x < len(ter_codes) - 1 else "")
    )

_add_line("  },")

########################################################################
#  Transaction type processing
########################################################################
_add_line('  "TRANSACTION_TYPES": {')

# Parse transaction types
# Example line:
# TRANSACTION(ttCHECK_CREATE, 16, CheckCreate, ({
tx_hits = re.findall(
    r"^ *TRANSACTION\(tt[A-Z_]+[ \n]*,[ \n]*([0-9]+)[ \n]*,[ \n]*([A-Za-z]+).*$",
    transactions_file,
    re.MULTILINE,
)
tx_hits.append(("-1", "Invalid"))
tx_hits.sort(key=lambda x: x[1])

for x in range(len(tx_hits)):
    _add_line(
        '    "'
        + tx_hits[x][1]
        + '": '
        + tx_hits[x][0]
        + ("," if x < len(tx_hits) - 1 else "")
    )

_add_line("  },")

########################################################################
#  Serialized type processing
########################################################################
_add_line('  "TYPES": {')

type_hits.append(("DONE", "-1"))
type_hits.sort(key=lambda x: _translate(x[0]))
for x in range(len(type_hits)):
    _add_line(
        '    "'
        + _translate(type_hits[x][0])
        + '": '
        + type_hits[x][1]
        + ("," if x < len(type_hits) - 1 else "")
    )

_add_line("  }")
_add_line("}")


########################################################################
#  FORMATS and FLAGS
#
#  These mirror how rippled builds the same keys in
#  src/xrpld/rpc/handlers/server_info/ServerDefinitions.cpp.
########################################################################

# SOElement::style() values, as emitted by the server_definitions RPC.
SOE_STYLE = {"SoeRequired": 0, "SoeOptional": 1, "SoeDefault": 2}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _define_block(text: str, name: str) -> str:
    """Return the body of a multi-line #define, joining continuation lines."""
    match = re.search(r"#define\s+" + re.escape(name) + r"\b[^\n]*", text)
    if not match:
        return ""
    lines = text[match.start() :].split("\n")
    body = []
    for line in lines:
        body.append(line)
        if not line.rstrip().endswith("\\"):
            break
    return "\n".join(body)


def _parse_soelements(block: str) -> list:
    """Parse `{sfField, SoeStyle}` entries, preserving their order."""
    elements = []
    for match in re.finditer(r"\{\s*sf(\w+)\s*,\s*(Soe\w+)", _strip_comments(block)):
        style = SOE_STYLE.get(match.group(2))
        if style is None:
            continue
        elements.append({"name": match.group(1), "optionality": style})
    return elements


def _parse_common_fields(cpp: str) -> list:
    """Parse a getCommonFields() definition from TxFormats/LedgerFormats."""
    match = re.search(r"getCommonFields\(\)\s*\{(.*?)\breturn\b", cpp, re.DOTALL)
    return _parse_soelements(match.group(1)) if match else []


def _macro_arg_blocks(text: str, macro: str) -> list:
    """Yield the argument text of each top-level `MACRO(...)` entry.

    Also matches suffixed variants such as `LEDGER_ENTRY_DUPLICATE`, which
    rippled uses when a ledger entry and a transaction share a name.
    """
    blocks = []
    for match in re.finditer(
        r"^" + re.escape(macro) + r"(?:_\w+)?\(", text, re.MULTILINE
    ):
        depth, i = 0, match.end() - 1
        while i < len(text):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        blocks.append(text[match.end() : i])
    return blocks


def _parse_formats(macro_text: str, macro: str, common: list) -> dict:
    """Build a FORMATS map, omitting fields already listed as common."""
    common_names = {field["name"] for field in common}
    formats = {"common": common}
    for block in _macro_arg_blocks(macro_text, macro):
        name_match = re.match(r"\s*\w+\s*,\s*[^,]+,\s*(\w+)\s*,", block)
        if not name_match:
            continue
        template_start = block.rfind("({")
        if template_start == -1:
            continue
        fields = _parse_soelements(block[template_start:])
        formats[name_match.group(1)] = [
            f for f in fields if f["name"] not in common_names
        ]
    return formats


def _flag_symbols(*headers: str) -> dict:
    """Collect flag constants so symbolic references can be resolved.

    Some flags are defined by reference, e.g. `TF_FLAG(tfMPTCanLock,
    lsfMPTCanLock)`, where the value lives in LedgerFormats.h.
    """
    symbols = {}
    for header in headers:
        text = _strip_comments(header)
        for match in re.finditer(
            r"\b(?:TF_FLAG2?|LSF_FLAG2?|ASF_FLAG)\(\s*(\w+)\s*,\s*"
            r"(0[xX][0-9a-fA-F]+|\d+)\s*\)",
            text,
        ):
            symbols[match.group(1)] = int(match.group(2), 0)
        for match in re.finditer(
            r"\bconstexpr\s+\w+\s+(\w+)\s*=\s*(0[xX][0-9a-fA-F]+|\d+)\s*;", text
        ):
            symbols[match.group(1)] = int(match.group(2), 0)
    return symbols


def _parse_flag_groups(
    header: str, entry_macro: str, flag_macros: tuple, symbols: dict
) -> dict:
    """Parse the XMACRO flag table into {TypeName: {flagName: value}}."""
    block = _strip_comments(_define_block(header, "XMACRO"))
    groups = {}
    for part in re.split(r"\b" + re.escape(entry_macro) + r"\(", block)[1:]:
        name_match = re.match(r"\s*(\w+)\s*,", part)
        if not name_match:
            continue
        flags = {}
        for flag_macro in flag_macros:
            pattern = (
                r"\b" + re.escape(flag_macro) + r"\(\s*(\w+)\s*,\s*([^,()]+?)\s*\)"
            )
            for flag in re.finditer(pattern, part):
                raw = flag.group(2).strip()
                if re.fullmatch(r"0[xX][0-9a-fA-F]+|\d+", raw):
                    flags[flag.group(1)] = int(raw, 0)
                elif raw in symbols:
                    flags[flag.group(1)] = symbols[raw]
                else:
                    print(
                        f"Warning: unresolved flag value {flag.group(1)} = {raw}",
                        file=sys.stderr,
                    )
        groups[name_match.group(1)] = flags
    return groups


def _parse_constexpr_flag(header: str, name: str) -> int:
    match = re.search(
        r"\b" + re.escape(name) + r"\s*=\s*(0[xX][0-9a-fA-F]+|\d+)", header
    )
    return int(match.group(1), 0) if match else 0


def _parse_asf_flags(header: str) -> dict:
    block = _strip_comments(_define_block(header, "ACCOUNTSET_FLAGS"))
    return {
        m.group(1): int(m.group(2), 0)
        for m in re.finditer(
            r"\bASF_FLAG\(\s*(\w+)\s*,\s*(0[xX][0-9a-fA-F]+|\d+)\s*\)", block
        )
    }


definitions = json.loads(output)

definitions["TRANSACTION_FORMATS"] = _parse_formats(
    transactions_file, "TRANSACTION", _parse_common_fields(tx_formats_cpp)
)
definitions["LEDGER_ENTRY_FORMATS"] = _parse_formats(
    ledger_entries_file, "LEDGER_ENTRY", _parse_common_fields(ledger_formats_cpp)
)

# rippled lists a "universal" group ahead of the per-transaction groups.
tx_flags = {
    "universal": {
        "tfFullyCanonicalSig": _parse_constexpr_flag(tx_flags_h, "tfFullyCanonicalSig"),
        "tfInnerBatchTxn": _parse_constexpr_flag(tx_flags_h, "tfInnerBatchTxn"),
    }
}
flag_symbols = _flag_symbols(ledger_formats_h, tx_flags_h)
tx_flags.update(
    _parse_flag_groups(tx_flags_h, "TRANSACTION", ("TF_FLAG", "TF_FLAG2"), flag_symbols)
)
definitions["TRANSACTION_FLAGS"] = tx_flags

definitions["LEDGER_ENTRY_FLAGS"] = _parse_flag_groups(
    ledger_formats_h, "LEDGER_OBJECT", ("LSF_FLAG", "LSF_FLAG2"), flag_symbols
)
definitions["ACCOUNT_SET_FLAGS"] = _parse_asf_flags(tx_flags_h)

# "hash" is a digest rippled computes over its own structures and cannot be
# derived from source, so it is omitted here. Nothing in the library reads it.
output = json.dumps(definitions, indent=2, sort_keys=True) + "\n"


if len(sys.argv) == 3:
    output_file = sys.argv[2]
else:
    output_file = os.path.join(
        os.path.dirname(__file__),
        "../xrpl/core/binarycodec/definitions/definitions.json",
    )

with open(output_file, "w") as f:
    f.write(output)
print("File written successfully to " + output_file)
