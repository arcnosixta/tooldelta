"""Conservative local contract checks, with explicit review for unsupported semantics."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from .catalog import normalize_catalog

SEVERITIES = ("breaking", "review", "info")
ANNOTATIONS = {"title", "description", "default", "examples", "deprecated", "readOnly", "writeOnly", "$schema", "$id", "$comment"}
SUPPORTED = {"type", "properties", "required", "additionalProperties", "items", "enum", "const", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties", "uniqueItems"} | ANNOTATIONS
MISSING = object()


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(tools: dict[str, dict[str, Any]]) -> str:
    """Order-independent catalog identity, including descriptions and extensions."""
    return hashlib.sha256(_json(tools).encode("utf-8")).hexdigest()


def pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


@dataclass(frozen=True)
class Change:
    severity: str
    code: str
    tool: str
    path: str
    message: str
    action: str
    before: Any = None
    after: Any = None


@dataclass(frozen=True)
class Report:
    changes: tuple[Change, ...]
    old_count: int
    new_count: int
    old_hash: str
    new_hash: str

    @property
    def counts(self) -> dict[str, int]:
        return {severity: sum(c.severity == severity for c in self.changes) for severity in SEVERITIES}

    def fails(self, threshold: str = "breaking") -> bool:
        if threshold == "none":
            return False
        return any(self.counts[s] for s in SEVERITIES[:SEVERITIES.index(threshold) + 1])

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": 1, "summary": self.counts,
                "catalogs": {"before": {"tools": self.old_count, "sha256": self.old_hash},
                             "after": {"tools": self.new_count, "sha256": self.new_hash}},
                "changes": [asdict(change) for change in self.changes]}


class _Comparator:
    def __init__(self) -> None:
        self.changes: list[Change] = []

    def add(self, severity: str, code: str, tool: str, path: str, message: str,
            action: str, before: Any = None, after: Any = None) -> None:
        self.changes.append(Change(severity, code, tool, path, message, action,
                                   None if before is MISSING else before,
                                   None if after is MISSING else after))

    def schema(self, old: Any, new: Any, tool: str, path: str, output: bool = False) -> None:
        # Accepted producer values must remain valid for the consumer.
        # Inputs: old calls -> new server. Outputs: new server -> old consumer.
        source, target = (new, old) if output else (old, new)
        subject = "New responses" if output else "Previously valid calls"
        action = ("Update consumers and verify representative response fixtures." if output
                  else "Update callers or preserve the previous accepted input contract.")

        def emit(severity: str, code: str, key: str, message: str,
                 before: Any = MISSING, after: Any = MISSING) -> None:
            if output:
                before, after = after, before
            self.add(severity, code, tool, path + ("/" + key if key else ""),
                     message, action, before, after)

        if isinstance(source, bool) or isinstance(target, bool):
            if source != target:
                narrowing = target is False or source is True
                emit("breaking" if narrowing else "info", "schema.acceptance", "",
                     f"{subject} {'may be rejected' if narrowing else 'remain accepted'} by a boolean schema change.", source, target)
            # Inspect the object side too: unsupported keywords must never disappear silently.
            for schema in (old, new):
                if isinstance(schema, dict):
                    self.unsupported(schema, tool, path)
            return

        self.unsupported_pair(old, new, tool, path)
        source_types, target_types = self.types(source), self.types(target)
        if source_types != target_types:
            # integer is a subset of number, not an unrelated type.
            if not source_types <= target_types:
                emit("breaking", "schema.type", "type", f"{subject} may use a type the consumer no longer accepts.", source.get("type"), target.get("type"))
            else:
                emit("info", "schema.type", "type", "Accepted types widened in the compatibility direction.", source.get("type"), target.get("type"))

        source_values, target_values = self.values(source), self.values(target)
        if source_values != target_values:
            if target_values is not None and (source_values is None or not source_values <= target_values):
                emit("breaking", "schema.values", "enum" if "enum" in old or "enum" in new else "const",
                     f"{subject} may contain a value excluded by enum/const.", self.value_display(source), self.value_display(target))
            else:
                emit("info", "schema.values", "enum" if "enum" in old or "enum" in new else "const",
                     "Allowed values widened in the compatibility direction.", self.value_display(source), self.value_display(target))

        src_required = set(source.get("required", []))
        dst_required = set(target.get("required", []))
        for name in sorted(dst_required - src_required):
            emit("breaking", "schema.required", "required/" + pointer(name),
                 f"{subject} may omit required property {name!r}.", name in src_required, name in dst_required)
        for name in sorted(src_required - dst_required):
            emit("info", "schema.required", "required/" + pointer(name),
                 f"Property {name!r} is no longer required in the compatibility direction.", True, False)

        for key in ("minimum", "exclusiveMinimum", "minLength", "minItems", "minProperties",
                    "maximum", "exclusiveMaximum", "maxLength", "maxItems", "maxProperties"):
            a, b = source.get(key), target.get(key)
            if a == b:
                continue
            lower = key.startswith("min") or key == "exclusiveMinimum"
            tighter = b is not None and (a is None or (b > a if lower else b < a))
            emit("breaking" if tighter else "info", "schema.bound", key,
                 f"{key} {'tightened; ' + subject.lower() + ' may violate the new bound' if tighter else 'relaxed in the compatibility direction'}.", a, b)

        if source.get("uniqueItems", False) != target.get("uniqueItems", False):
            tighter = target.get("uniqueItems", False)
            emit("breaking" if tighter else "info", "schema.unique", "uniqueItems",
                 "Array uniqueness requirement changed.", source.get("uniqueItems", False), tighter)

        src_props, dst_props = source.get("properties", {}), target.get("properties", {})
        src_extra, dst_extra = source.get("additionalProperties", True), target.get("additionalProperties", True)
        for name in sorted(src_props.keys() | dst_props.keys()):
            child_path = path + "/properties/" + pointer(name)
            if name in src_props and name in dst_props:
                a, b = (dst_props[name], src_props[name]) if output else (src_props[name], dst_props[name])
                self.schema(a, b, tool, child_path, output)
            elif name in src_props:
                if dst_extra is False:
                    emit("breaking", "schema.property", "properties/" + pointer(name),
                         f"{subject} may include now-forbidden property {name!r}.", src_props[name], MISSING)
                elif isinstance(dst_extra, dict):
                    a, b = (dst_extra, src_props[name]) if output else (src_props[name], dst_extra)
                    self.schema(a, b, tool, child_path, output)
                else:
                    emit("review", "schema.property", "properties/" + pointer(name),
                         f"Property {name!r} lost its explicit contract; check server and caller behavior.", src_props[name], MISSING)
            else:
                if src_extra is False:
                    emit("info", "schema.property", "properties/" + pointer(name),
                         f"Property {name!r} is newly accepted in the compatibility direction.", MISSING, dst_props[name])
                else:
                    # Previously accepted extras are now constrained by an explicit property schema.
                    a, b = (dst_props[name], src_extra) if output else (src_extra, dst_props[name])
                    self.schema(a, b, tool, child_path, output)

        # Additional-property rules change their domain when named properties change.
        # Report that ambiguity instead of asserting a proof of full compatibility.
        if src_extra != dst_extra:
            if src_props.keys() != dst_props.keys():
                emit("review", "schema.additional", "additionalProperties",
                     "Additional-property policy and named properties changed together; review their interaction.", src_extra, dst_extra)
            else:
                a, b = (dst_extra, src_extra) if output else (src_extra, dst_extra)
                self.schema(a, b, tool, path + "/additionalProperties", output)

        if "items" in source or "items" in target:
            a, b = source.get("items", True), target.get("items", True)
            if output:
                a, b = b, a
            self.schema(a, b, tool, path + "/items", output)

        for key in sorted(ANNOTATIONS):
            a, b = old.get(key, MISSING), new.get(key, MISSING)
            if a != b:
                self.add("info", "schema.metadata", tool, path + "/" + pointer(key),
                         f"Schema metadata {key!r} changed.", "Review generated documentation and defaults.", a, b)

    @staticmethod
    def types(schema: dict[str, Any]) -> set[str]:
        value = schema.get("type", ["null", "boolean", "object", "array", "number", "integer", "string"])
        result = set([value] if isinstance(value, str) else value)
        if "number" in result:
            result.add("integer")
        return result

    @staticmethod
    def values(schema: dict[str, Any]) -> set[str] | None:
        values = {_json(v) for v in schema["enum"]} if "enum" in schema else None
        if "const" in schema:
            const = {_json(schema["const"])}
            values = const if values is None else values & const
        return values

    @staticmethod
    def value_display(schema: dict[str, Any]) -> Any:
        return {key: schema[key] for key in ("enum", "const") if key in schema} or None

    def unsupported(self, schema: dict[str, Any], tool: str, path: str) -> None:
        for key in sorted(schema.keys() - SUPPORTED):
            self.add("review", "schema.unsupported", tool, path + "/" + pointer(key),
                     f"Keyword {key!r} requires manual semantic review, even when unchanged.",
                     "Use a full JSON Schema validator and representative fixtures; references are never resolved.", schema[key], schema[key])

    def unsupported_pair(self, old: dict[str, Any], new: dict[str, Any], tool: str, path: str) -> None:
        for key in sorted((old.keys() | new.keys()) - SUPPORTED):
            self.add("review", "schema.unsupported", tool, path + "/" + pointer(key),
                     f"Keyword {key!r} requires manual semantic review, even when unchanged.",
                     "Use a full JSON Schema validator and representative fixtures; references are never resolved.", old.get(key), new.get(key))


def compare(before: Any, after: Any) -> Report:
    """Compare catalogs, not server behavior. Unknown semantics always require review."""
    old, new = normalize_catalog(before), normalize_catalog(after)
    engine = _Comparator()
    for name in sorted(old.keys() - new.keys()):
        engine.add("breaking", "tool.removed", name, "", "Tool was removed; existing calls cannot resolve it.", "Migrate callers or keep a compatibility alias.", old[name], None)
    for name in sorted(new.keys() - old.keys()):
        engine.add("info", "tool.added", name, "", "Tool was added.", "Review whether agents should be allowed to discover this tool.", None, new[name])
        # Newly added tools can still contain unsupported semantics.
        engine.schema(new[name]["inputSchema"], new[name]["inputSchema"], name, "/inputSchema")
        if "outputSchema" in new[name]:
            engine.schema(new[name]["outputSchema"], new[name]["outputSchema"], name, "/outputSchema", True)
    known = {"name", "inputSchema", "outputSchema", "description", "title", "annotations"}
    for name in sorted(old.keys() & new.keys()):
        a, b = old[name], new[name]
        engine.schema(a["inputSchema"], b["inputSchema"], name, "/inputSchema")
        if "outputSchema" in a and "outputSchema" in b:
            engine.schema(a["outputSchema"], b["outputSchema"], name, "/outputSchema", True)
        elif "outputSchema" in a:
            engine.add("breaking", "output.removed", name, "/outputSchema", "Declared output guarantees were removed.", "Restore the output contract or migrate consumers.", a["outputSchema"], None)
        elif "outputSchema" in b:
            engine.add("info", "output.added", name, "/outputSchema", "An output contract was added.", "Check structured response fixtures against the declared schema.", None, b["outputSchema"])
            engine.schema(b["outputSchema"], b["outputSchema"], name, "/outputSchema", True)
        for key in ("description", "title"):
            if a.get(key) != b.get(key):
                engine.add("review" if key == "description" else "info", "tool." + key, name, "/" + key,
                           f"Tool {key} changed" + ("; agent tool selection may change." if key == "description" else "."),
                           "Review intent and re-run tool selection evaluations.", a.get(key), b.get(key))
        annotations_a, annotations_b = a.get("annotations", {}), b.get("annotations", {})
        for key in sorted(annotations_a.keys() | annotations_b.keys()):
            if annotations_a.get(key, MISSING) != annotations_b.get(key, MISSING):
                engine.add("info" if key == "title" else "review", "tool.annotation", name, "/annotations/" + pointer(key),
                           f"Declared {key} changed; annotations are untrusted hints, not enforced permissions.",
                           "Review actual server behavior and agent approval policy.", annotations_a.get(key), annotations_b.get(key))
        for key in sorted((a.keys() | b.keys()) - known):
            if a.get(key, MISSING) != b.get(key, MISSING):
                engine.add("review", "tool.extension", name, "/" + pointer(key), "Extension metadata changed; semantics are unknown.", "Review the extension contract with its producer.", a.get(key), b.get(key))
    changes = tuple(sorted(engine.changes, key=lambda c: (SEVERITIES.index(c.severity), c.tool, c.path, c.code)))
    return Report(changes, len(old), len(new), fingerprint(old), fingerprint(new))
