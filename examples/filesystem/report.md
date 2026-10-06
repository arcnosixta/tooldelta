# ToolDelta contract report

**2025.1.14.json → 2026.8.31.json**

1 breaking · 45 review · 41 info

| Level | Tool | Path | Change | Action |
| --- | --- | --- | --- | --- |
| breaking | read\_multiple\_files | /inputSchema/properties/paths/minItems | minItems tightened; previously valid calls may violate the new bound. | Update callers or preserve the previous accepted input contract. |
| review | create\_directory | /annotations/destructiveHint | Declared destructiveHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | create\_directory | /annotations/idempotentHint | Declared idempotentHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | create\_directory | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | create\_directory | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | create\_directory | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | directory\_tree | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | directory\_tree | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | directory\_tree | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | edit\_file | /annotations/destructiveHint | Declared destructiveHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | edit\_file | /annotations/idempotentHint | Declared idempotentHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | edit\_file | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | edit\_file | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | edit\_file | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | get\_file\_info | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | get\_file\_info | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | get\_file\_info | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | list\_allowed\_directories | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | list\_allowed\_directories | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | list\_allowed\_directories | /description | Tool description changed; agent tool selection may change. | Review intent and re-run tool selection evaluations. |
| review | list\_allowed\_directories | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | list\_directory | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | list\_directory | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | list\_directory | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | move\_file | /annotations/destructiveHint | Declared destructiveHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | move\_file | /annotations/idempotentHint | Declared idempotentHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | move\_file | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | move\_file | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | move\_file | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | read\_file | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | read\_file | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | read\_file | /description | Tool description changed; agent tool selection may change. | Review intent and re-run tool selection evaluations. |
| review | read\_file | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | read\_media\_file | /outputSchema/properties/content/items/anyOf | Keyword &#x27;anyOf&#x27; requires manual semantic review, even when unchanged. | Use a full JSON Schema validator and representative fixtures; references are never resolved. |
| review | read\_multiple\_files | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | read\_multiple\_files | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | read\_multiple\_files | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | search\_files | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | search\_files | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | search\_files | /description | Tool description changed; agent tool selection may change. | Review intent and re-run tool selection evaluations. |
| review | search\_files | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| review | write\_file | /annotations/destructiveHint | Declared destructiveHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | write\_file | /annotations/idempotentHint | Declared idempotentHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | write\_file | /annotations/openWorldHint | Declared openWorldHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | write\_file | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | write\_file | /execution | Extension metadata changed; semantics are unknown. | Review the extension contract with its producer. |
| info | create\_directory | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | create\_directory | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | create\_directory | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | directory\_tree | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | directory\_tree | /inputSchema/properties/excludePatterns | Property &#x27;excludePatterns&#x27; is newly accepted in the compatibility direction. | Update callers or preserve the previous accepted input contract. |
| info | directory\_tree | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | directory\_tree | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | edit\_file | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | edit\_file | /inputSchema/properties/edits/items/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | edit\_file | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | edit\_file | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | get\_file\_info | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | get\_file\_info | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | get\_file\_info | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | list\_allowed\_directories | /inputSchema/$schema | Schema metadata &#x27;$schema&#x27; changed. | Review generated documentation and defaults. |
| info | list\_allowed\_directories | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | list\_allowed\_directories | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | list\_directory | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | list\_directory | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | list\_directory | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | list\_directory\_with\_sizes | / | Tool was added. | Review whether agents should be allowed to discover this tool. |
| info | move\_file | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | move\_file | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | move\_file | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | read\_file | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | read\_file | /inputSchema/properties/head | Property &#x27;head&#x27; is newly accepted in the compatibility direction. | Update callers or preserve the previous accepted input contract. |
| info | read\_file | /inputSchema/properties/tail | Property &#x27;tail&#x27; is newly accepted in the compatibility direction. | Update callers or preserve the previous accepted input contract. |
| info | read\_file | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | read\_file | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | read\_media\_file | / | Tool was added. | Review whether agents should be allowed to discover this tool. |
| info | read\_multiple\_files | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | read\_multiple\_files | /inputSchema/properties/paths/description | Schema metadata &#x27;description&#x27; changed. | Review generated documentation and defaults. |
| info | read\_multiple\_files | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | read\_multiple\_files | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | read\_text\_file | / | Tool was added. | Review whether agents should be allowed to discover this tool. |
| info | search\_files | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | search\_files | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | search\_files | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |
| info | write\_file | /inputSchema/additionalProperties | Previously valid calls remain accepted by a boolean schema change. | Update callers or preserve the previous accepted input contract. |
| info | write\_file | /outputSchema | An output contract was added. | Check structured response fixtures against the declared schema. |
| info | write\_file | /title | Tool title changed. | Review intent and re-run tool selection evaluations. |

Offline static comparison. Annotations are untrusted hints. Review unsupported semantics; this is not a safety certificate.

Baseline SHA-256: `a6a2eb6b486a198d43f5322d0f61257f0d506164227669732921e06bab6743a2`

Candidate SHA-256: `b09c12887c7d62491e81be9c556f240691368ea6744d3a299de242aeb96d5d61`
