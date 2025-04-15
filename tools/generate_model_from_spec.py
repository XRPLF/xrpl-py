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
                # TODO: add map from spec type to xrpl-py type
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


def _generate_error_line(field_name: str, error_msg: str) -> str:
    return f'errors["{field_name}"] = "{error_msg}"'


with open("../rippled-api-spec/shared/transactions/account_set.yaml", "r") as file:
    spec = yaml.safe_load(file)

output_str = ""
validations = []

schemas = spec["components"]["schemas"]
for schema_name, schema in schemas.items():
    class_name = schema_name
    if class_name.endswith("Transaction"):
        class_name = class_name[: -len("Transaction")]
    if class_name.endswith("Request"):
        class_name = class_name[: -len("Request")]

    inherited = _get_inherited_classes(schema.get("allOf", []))

    description = schema.get("description", "").strip()

    # TODO: consider using a jinja template to make this neater
    output_str += f"""\"\"\"
{description}
\"\"\"

from dataclasses import dataclass, field
# TODO: add imports

@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class {class_name}{"(" + ", ".join(inherited) + ")" if inherited else ""}:
    {description}

    transaction_type: TransactionType = field(
        default=TransactionType.{_key_to_json(class_name).upper()},
        init=False,
    )
    """

    required_fields = schema.get("required", [])
    for prop_name, property in schema.get("properties", {}).items():
        python_name = _to_snake_case(prop_name)
        type = _get_format(property)
        property_description = (
            property.get("description", "").strip().replace("\n", "\n    ")
        )
        default = "REQUIRED" if prop_name in required_fields else "None"
        for validation_field in ["maxLength", "minLength", "maximum", "minimum"]:
            if validation_field in property:
                validations.append(
                    [validation_field, python_name, property[validation_field]]
                )

        output_str += f"""
    {python_name}: {type} = {default}
    """
        if property_description != "":
            output_str += f'"""\n    {property_description}\n    """\n'

    if len(validations) > 0:
        output_str += """
    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
"""
        for validation in validations:
            val_type, prop_name, value = validation
            if val_type == "maxLength":
                output_str += f"""
        if len(self.{prop_name}) > {value}:
            {_generate_error_line(prop_name, f"Length cannot be more than {value}.")}"""
            elif val_type == "minLength":
                output_str += f"""
        if len(self.{prop_name}) < {value}:
            {_generate_error_line(prop_name, f"Length cannot be less than {value}.")}"""
            if val_type == "maximum":
                output_str += f"""
        if self.{prop_name} > {value}:
            {_generate_error_line(prop_name, f"Value cannot be more than {value}.")}"""
            elif val_type == "minimum":
                output_str += f"""
        if self.{prop_name} < {value}:
            {_generate_error_line(prop_name, f"Value cannot be less than {value}.")}"""

        output_str += "\n\n        return errors\n"

    pprint(schema)

    break

print("----")
print(output_str)
