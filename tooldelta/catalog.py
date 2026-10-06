"""Strict, bounded loading of saved tools/list catalogs. Never executes tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_BYTES = 8 * 1024 * 1024
MAX_DEPTH = 64
TYPES = {"null", "boolean", "object", "array", "number", "integer", "string"}


class CatalogError(ValueError):
    """The input is not a supported, structurally valid tool catalog."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError("Duplicate JSON object key; remove ambiguous entries.")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise CatalogError("Non-finite numbers are not valid JSON.")


def _depth(value: Any, level: int = 0) -> None:
    if level > MAX_DEPTH:
        raise CatalogError(f"Input nesting exceeds {MAX_DEPTH} levels.")
    if isinstance(value, dict):
        for item in value.values():
            _depth(item, level + 1)
    elif isinstance(value, list):
        for item in value:
            _depth(item, level + 1)


def validate_schema(schema: Any, location: str, root: bool = False) -> None:
    if isinstance(schema, bool) and not root:
        return
    if not isinstance(schema, dict):
        raise CatalogError(f"{location}: schema must be an object.")
    if root and schema.get("type") != "object":
        raise CatalogError(f"{location}: MCP root schema must have type 'object'.")
    if "type" in schema:
        types = schema["type"]
        values = [types] if isinstance(types, str) else types
        if (not isinstance(values, list) or not values
                or any(not isinstance(v, str) or v not in TYPES for v in values)
                or len(set(values)) != len(values)):
            raise CatalogError(f"{location}: invalid JSON Schema type.")
    for key in ("title", "description", "$ref", "$schema", "$id", "pattern", "format"):
        if key in schema and not isinstance(schema[key], str):
            raise CatalogError(f"{location}: {key} must be a string.")
    for key in ("properties", "$defs", "definitions", "patternProperties", "dependentSchemas"):
        if key in schema:
            if not isinstance(schema[key], dict):
                raise CatalogError(f"{location}: {key} must be an object.")
            for name, child in schema[key].items():
                validate_schema(child, f"{location}/{key}/{name}")
    if "required" in schema:
        required = schema["required"]
        if (not isinstance(required, list) or any(not isinstance(v, str) for v in required)
                or len(set(required)) != len(required)):
            raise CatalogError(f"{location}: required must contain unique strings.")
    if "enum" in schema:
        enum = schema["enum"]
        if not isinstance(enum, list) or not enum:
            raise CatalogError(f"{location}: enum must be a non-empty array.")
        if len({value_key(v) for v in enum}) != len(enum):
            raise CatalogError(f"{location}: enum values must be unique.")
    for key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"):
        if key in schema and (isinstance(schema[key], bool)
                              or not isinstance(schema[key], (float, int))):
            raise CatalogError(f"{location}: {key} must be a number.")
    if "multipleOf" in schema and schema["multipleOf"] <= 0:
        raise CatalogError(f"{location}: multipleOf must be positive.")
    for key in ("minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            raise CatalogError(f"{location}: {key} must be a non-negative integer.")
    for key in ("uniqueItems", "readOnly", "writeOnly", "deprecated"):
        if key in schema and not isinstance(schema[key], bool):
            raise CatalogError(f"{location}: {key} must be boolean.")
    for key in ("items", "additionalProperties", "not", "if", "then", "else", "contains", "propertyNames", "unevaluatedProperties", "unevaluatedItems"):
        if key in schema:
            validate_schema(schema[key], f"{location}/{key}")
    for key in ("allOf", "anyOf", "oneOf", "prefixItems"):
        if key in schema:
            if not isinstance(schema[key], list) or not schema[key]:
                raise CatalogError(f"{location}: {key} must be a non-empty schema array.")
            for index, child in enumerate(schema[key]):
                validate_schema(child, f"{location}/{key}/{index}")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def value_key(value: Any) -> str:
    """JSON Schema equality: 1 equals 1.0, but neither equals true."""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    elif isinstance(value, list):
        return "[" + ",".join(value_key(item) for item in value) + "]"
    elif isinstance(value, dict):
        return "{" + ",".join(_canonical(key) + ":" + value_key(item)
                              for key, item in sorted(value.items())) + "}"
    return _canonical(value)


def normalize_catalog(data: Any) -> dict[str, dict[str, Any]]:
    """Accept bare arrays, {tools: [...]}, or JSON-RPC {result: {tools: [...]}}."""
    try:
        _depth(data)
        _canonical(data)
    except (RecursionError, ValueError) as exc:
        raise CatalogError("Input is too deeply nested or contains invalid JSON values.") from exc
    if isinstance(data, dict):
        if "error" in data:
            raise CatalogError("JSON-RPC error response is not a tool catalog.")
        data = data.get("result", data)
        if not isinstance(data, dict):
            raise CatalogError("JSON-RPC result must be an object.")
        if data.get("nextCursor") is not None:
            raise CatalogError("Paginated catalog is incomplete. Merge all pages and remove nextCursor.")
        data = data.get("tools")
    if not isinstance(data, list):
        raise CatalogError("Expected tools array, {tools: [...]}, or {result: {tools: [...]}}.")
    tools: dict[str, dict[str, Any]] = {}
    for index, tool in enumerate(data):
        if not isinstance(tool, dict) or not isinstance(tool.get("name"), str) or not tool["name"]:
            raise CatalogError(f"Tool {index}: a non-empty string name is required.")
        name = tool["name"]
        if name in tools:
            raise CatalogError("Duplicate tool name; catalogs must contain unique tools.")
        for key in ("description", "title"):
            if key in tool and not isinstance(tool[key], str):
                raise CatalogError(f"Tool {index}: {key} must be a string.")
        validate_schema(tool.get("inputSchema"), f"tool[{index}]/inputSchema", root=True)
        if "outputSchema" in tool:
            validate_schema(tool["outputSchema"], f"tool[{index}]/outputSchema", root=True)
        if "annotations" in tool:
            annotations = tool["annotations"]
            if not isinstance(annotations, dict):
                raise CatalogError(f"Tool {index}: annotations must be an object.")
            for key in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
                if key in annotations and not isinstance(annotations[key], bool):
                    raise CatalogError(f"Tool {index}: {key} must be boolean.")
        tools[name] = tool
    return dict(sorted(tools.items()))


def load_catalog(path: str | Path) -> dict[str, dict[str, Any]]:
    """Read at most 8 MiB; reject duplicate keys, partial responses and invalid JSON."""
    try:
        with Path(path).open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise CatalogError("Catalog exceeds the 8 MiB input limit.")
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_pairs, parse_constant=_constant)
        return normalize_catalog(data)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError("Catalog must be valid UTF-8 JSON.") from exc
    except RecursionError as exc:
        raise CatalogError("Catalog nesting is too deep.") from exc
