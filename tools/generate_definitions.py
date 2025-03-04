"""Script to generate the definitions.json file from rippled source code."""

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


# Translate from rippled string format to what the binary codecs expect
def _translate(inp: str) -> str:
    if re.match(r"^UINT", inp):
        if re.search(r"256|160|128|192", inp):
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
_add_line(
    """    [
      "Generic",
      {
        "isSerialized": false,
        "isSigningField": false,
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
    ],"""
)

# Parse STypes
# Example line:
# STYPE(STI_UINT32, 2)    \
type_hits = re.findall(
    r"^ *STYPE\(STI_([^ ]*?) *, *([0-9-]+) *\) *\\?$", sfield_h, re.MULTILINE
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
    if not_signing_field == "notSigning":
        return "false"
    if t == "LEDGERENTRY" or t == "TRANSACTION" or t == "VALIDATION" or t == "METADATA":
        return "false"
    return "true"


# Parse SField.cpp for all the SFields and their serialization info
# Example lines:
# TYPED_SFIELD(sfFee, AMOUNT, 8)
# UNTYPED_SFIELD(sfSigners,  ARRAY, 3, SField::sMD_Default, SField::notSigning)
sfield_hits = re.findall(
    r"^ *[A-Z]*TYPED_SFIELD *\( *sf([^,\n]*),[ \n]*([^, \n]+)[ \n]*,[ \n]*"
    r"([0-9]+)(,.*?(notSigning))?",
    sfield_macro_file,
    re.MULTILINE,
)
sfield_hits += [
    ("hash", "UINT256", "257", "", "notSigning"),
    ("index", "UINT256", "258", "", "notSigning"),
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
    r"^ *LEDGER_ENTRY[A-Z_]*\(lt[A-Z_]+ *, *([xX0-9a-fA-F]+) *, *([^,]+), *([^,]+), "
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
    r"^ *((tel|tem|tef|ter|tes|tec)[A-Z_]+)( *= *([0-9-]+))? *,? *(\/\/[^\n]*)?$",
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
    r"^ *TRANSACTION\(tt[A-Z_]+ *,* ([0-9]+) *, *([A-Za-z]+).*$",
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
