"""Script to generate transaction models from rippled API spec."""

from pprint import pprint
from typing import Any, Dict, List

import yaml

from xrpl.models.base_model import _key_to_json


def _to_snake_case(name: str) -> str:
    return _key_to_json(name)


def _get_inherited_classes(allof: List[Dict[str, Any]]) -> List[str]:
    inherited = []
    for item in allof:
        if "$ref" in item:
            ref = item["$ref"]
            if ref.startswith("../base.yaml#/components/schemas/"):
                ref = ref[len("../base.yaml#/components/schemas/") :]
            inherited.append(ref)
        else:
            raise ValueError("WTFFFFFFFFFFFF " + str(item))
    return inherited


def _get_format(schema: Dict[str, Any]) -> str:
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/components/schemas/"):
            ref = ref[len("#/components/schemas/") :]
        return ref
    if "type" in schema:
        type = schema["type"]
        if type == "string":
            # TODO: add map from spec type to xrpl-py type
            return schema.get("format", "string")
        elif type == "integer":
            return schema.get("format", "int")
        elif type == "number":
            return schema.get("format", "float")
        elif type == "boolean":
            return schema.get("format", "boolean")
    raise ValueError(f"Unknown schema format: {str(schema)}")


with open("../rippled-api-spec/shared/transactions/account_set.yaml", "r") as file:
    spec = yaml.safe_load(file)

output_str = ""

schemas = spec["components"]["schemas"]
for schema_name, schema in schemas.items():
    class_name = schema_name
    if class_name.endswith("Transaction"):
        class_name = class_name[: -len("Transaction")]
    if class_name.endswith("Request"):
        class_name = class_name[: -len("Request")]

    inherited = _get_inherited_classes(schema.get("allOf", []))

    description = schema.get("description", "").strip()

    output_str += f"""
{description}

class {class_name}{"(" + ", ".join(inherited) + ")" if inherited else ""}:
    {description}
    """

    required_fields = schema.get("required", [])
    for property_name, property in schema.get("properties", {}).items():
        python_name = _to_snake_case(property_name)
        type = _get_format(property)
        description = property.get("description", "").strip().replace("\n", "\n    ")
        default = "REQUIRED" if property_name in required_fields else "None"
        output_str += f"""
    {python_name}: {type} = {default}
    """
        if description != "":
            output_str += f'"""\n    {description}\n    """\n'

    pprint(schema)

    break

print("----")
print(output_str)
