# ToolDelta contract report

**workspace v1.4 → workspace v1.5**

4 breaking · 3 review · 3 info

| Level | Tool | Path | Change | Action |
| --- | --- | --- | --- | --- |
| breaking | list\_projects | / | Tool was removed; existing calls cannot resolve it. | Migrate callers or keep a compatibility alias. |
| breaking | search\_documents | /inputSchema/properties/limit/maximum | maximum tightened; previously valid calls may violate the new bound. | Update callers or preserve the previous accepted input contract. |
| breaking | search\_documents | /inputSchema/required/workspace\_id | Previously valid calls may omit required property &#x27;workspace\_id&#x27;. | Update callers or preserve the previous accepted input contract. |
| breaking | search\_documents | /outputSchema/properties/status/enum | New responses may contain a value excluded by enum/const. | Update consumers and verify representative response fixtures. |
| review | read\_file | /annotations/destructiveHint | Declared destructiveHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | read\_file | /annotations/readOnlyHint | Declared readOnlyHint changed; annotations are untrusted hints, not enforced permissions. | Review actual server behavior and agent approval policy. |
| review | read\_file | /description | Tool description changed; agent tool selection may change. | Review intent and re-run tool selection evaluations. |
| info | create\_project | / | Tool was added. | Review whether agents should be allowed to discover this tool. |
| info | read\_file | /inputSchema/properties/normalize | Property &#x27;normalize&#x27; is newly accepted in the compatibility direction. | Update callers or preserve the previous accepted input contract. |
| info | search\_documents | /inputSchema/properties/workspace\_id | Property &#x27;workspace\_id&#x27; is newly accepted in the compatibility direction. | Update callers or preserve the previous accepted input contract. |

Offline static comparison. Annotations are untrusted hints. Review unsupported semantics; this is not a safety certificate.

Baseline SHA-256: `1113231e25aca1369105ffc9b020c17eef9920285739231cf005f30808dac192`

Candidate SHA-256: `c739d7875b2584dbf592ee367c807fd95ec0edf658fc84d5d94d49ce25846a06`
