"""Portable reports; HTML renders untrusted catalog strings with textContent only."""

from __future__ import annotations

import html
from importlib.resources import files
import json

from .diff import Report


def _safe_text(value: str) -> str:
    return "".join(char if char >= " " and char != "\x7f" else " " for char in value)


def _md(value: str) -> str:
    return html.escape(_safe_text(value)).replace("\\", "\\\\").replace("|", "\\|").replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")


def render(report: Report, format: str = "text", before: str = "baseline", after: str = "candidate") -> str:
    counts = report.counts
    if format == "json":
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    if format == "html":
        template = files("mcp_tooldelta").joinpath("templates/report.html").read_text(encoding="utf-8")
        payload = {**report.to_dict(), "labels": {"before": before, "after": after}}
        encoded = json.dumps(payload, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        return template.replace("__TOOLDELTA_PAYLOAD__", encoded)
    if format == "markdown":
        lines = ["# ToolDelta contract report", "", f"**{_md(before)} → {_md(after)}**", "",
                 f"{counts['breaking']} breaking · {counts['review']} review · {counts['info']} info", "",
                 "| Level | Tool | Path | Change | Action |", "| --- | --- | --- | --- | --- |"]
        for change in report.changes:
            lines.append("| " + " | ".join(_md(value) for value in (change.severity, change.tool, change.path or "/", change.message, change.action)) + " |")
        if not report.changes:
            lines += ["", "No contract changes detected in the supported schema subset."]
        lines += ["", "Offline static comparison. Annotations are untrusted hints. Review unsupported semantics; this is not a safety certificate.", "",
                  f"Baseline SHA-256: `{report.old_hash}`", "", f"Candidate SHA-256: `{report.new_hash}`", ""]
        return "\n".join(lines)
    if format != "text":
        raise ValueError(f"Unknown report format: {format}")
    lines = ["ToolDelta / MCP contract diff", f"{_safe_text(before)} -> {_safe_text(after)}", "",
             f"{counts['breaking']} breaking | {counts['review']} review | {counts['info']} info", ""]
    for change in report.changes:
        lines += [f"[{change.severity.upper()}] {_safe_text(change.tool)} {_safe_text(change.path) or '/'}",
                  "  " + _safe_text(change.message), "  Action: " + _safe_text(change.action), ""]
    if not report.changes:
        lines.append("No contract changes detected in the supported schema subset.")
    lines.append("Offline static comparison. Hints are not enforced permissions or a safety certificate.")
    return "\n".join(lines) + "\n"
