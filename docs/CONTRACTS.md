# Compatibility checks and boundaries

ToolDelta checks local contract differences. A `breaking` finding means a
constraint changed in a direction that **may** reject a formerly accepted call
or response. It does not prove the existence of such a call under every other
constraint. Other constraints may be redundant, contradictory, or outside scope.

Input direction: values accepted by the old server should remain accepted by the
new server. Output direction: values the new server promises to emit should fit
the old consumer's declared expectations. Output checks therefore reverse the
producer/consumer comparison. They apply to structured output contracts, not
unstructured text, image or resource content blocks.

| Change | Input | Output |
| --- | --- | --- |
| Tool removed | Breaking | Breaking |
| Required property added | Breaking | Info |
| Required property removed | Info | Breaking |
| Type number → integer | Breaking | Info |
| Type integer → number | Info | Breaking |
| Enum narrowed | Breaking | Info |
| Enum widened | Info | Breaking |
| Minimum increased / maximum decreased | Breaking | Info |
| Minimum decreased / maximum increased | Info | Breaking |
| uniqueItems false → true | Breaking | Info |
| Additional properties true → false, same named properties | Breaking | Info |
| Output schema removed | — | Breaking |
| Description or behavior hint changed | Review | Review |
| Unsupported schema keyword, including unchanged | Review | Review |

Supported keywords: `type`, `properties`, `required`, `additionalProperties`,
`items`, `enum`, `const`, `minimum`, `maximum`, `exclusiveMinimum`,
`exclusiveMaximum`, `minLength`, `maxLength`, `minItems`, `maxItems`,
`minProperties`, `maxProperties`, `uniqueItems`. Nested boolean schemas are
compared. Root schemas must be MCP object schemas. The structural checks follow
modern JSON Schema conventions, including numeric exclusive bounds and
schema-valued `items`; draft-04 boolean exclusive bounds and tuple-style `items`
arrays are not accepted.

## Objects and extras

Removing an input property from a closed object can reject existing calls.
Removing it from an open object is reviewed because the explicit field contract
disappeared, although extras may still be accepted. Adding an optional named
property to an open object can constrain values previously allowed as extras:
for example `{"q": 7}` becomes invalid if new `q` must be a string. This can be a
breaking change. Adding it to a previously closed object is an informational
extension, unless requiredness or unsupported semantics warrant a higher level.

When both the set of properties and the additional-property schema change, their
interaction is explicitly marked for review. ToolDelta does not solve the
complete language-inclusion problem for JSON Schema.

## Metadata and unknown semantics

Schema descriptions, defaults, examples and other non-validation metadata are
informational. Tool-level descriptions require review because they may affect
agent selection. All changed behavior annotations require review. These are
untrusted declarations; ToolDelta never asserts a tool is actually read-only,
destructive, idempotent, or restricted to a particular permission scope.

Unsupported validation keywords, including `$ref`, `$defs`, composition,
conditionals, `pattern`, `format`, `multipleOf`, `contains`, `prefixItems`, and
`unevaluatedProperties`, are review findings even if unchanged. References are
never fetched or resolved. A parent unsupported construct is reported as a unit;
its internal constraints are not analyzed. Schema extension keywords are also
reviewed. Tool-level extension metadata is reviewed when changed.

## Identity and JSON

Catalog hashing uses SHA-256 of compact UTF-8 JSON with sorted object keys and
tools sorted by name. Whitespace and tool order do not affect it. Array order
and numeric representation do: enum order or `1` versus `1.0` may change a hash
without changing the compatibility result. For enum/const semantics, numeric
integers and integral floats compare equally; JSON booleans remain distinct.
The entire tool object, including extension metadata, participates in the hash.

This is a reproducibility identity, not a cryptographic trust signature or an
artifact hash of the server executable. ToolDelta reads one local catalog at a
time. It cannot detect server behavior that is absent from the saved metadata.

## Report schema v1

JSON contains `schema_version`, severity counts under `summary`, baseline and
candidate counts/hashes under `catalogs`, and `changes`. Each change includes
`severity`, `code`, `tool`, `path`, `message`, `action`, `before`, and `after`.
Paths use JSON Pointer escaping; a required-property finding appends the property
name after `/required/` as a **semantic locator**, not an index into the original
required array. Missing values are rendered as null, so null and missing may not
be distinguishable in before/after previews. The message and code explain the change.

Messages and rule codes may evolve during the alpha. Consume severity and
`schema_version` for gating rather than matching English message text.

## Limits

No runtime calls, transport checks, package audits, prompt-injection detection,
authentication checks, real data validation, reference resolution, or full
JSON Schema meta-schema validation. Size/depth and structural validation help
reject malformed data, but do not certify an entire schema is logically valid.
No findings means no findings under these rules. It does not prove compatibility
or safety. Review representative fixtures and integration tests before updating
high-impact tools. Reports are local but may contain sensitive metadata.
