"""Capture tools/list from an explicitly selected stdio server; never calls tools.

This opt-in development script is separate from the offline ToolDelta runtime.
Pass a trusted command after --. The script starts that command as requested.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import subprocess
import threading
import time


def capture(command: list[str], timeout: int = 45) -> dict:
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding="utf-8")
    messages: queue.Queue = queue.Queue()
    diagnostics: list[str] = []

    def read_stdout():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except json.JSONDecodeError:
                messages.put({"invalid": True})
        messages.put({"closed": True})

    def read_stderr():
        for line in process.stderr:
            if len(diagnostics) < 20:
                diagnostics.append(line.strip())

    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()

    def send(message):
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    def receive(identifier):
        deadline = time.monotonic() + timeout
        while True:
            try:
                message = messages.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty as exc:
                raise RuntimeError("Timed out waiting for MCP response.") from exc
            if message.get("closed") or message.get("invalid"):
                raise RuntimeError("Server closed stdout or emitted invalid JSON: " + " ".join(diagnostics))
            if message.get("id") == identifier:
                if "error" in message:
                    raise RuntimeError("MCP error: " + json.dumps(message["error"]))
                return message["result"]
            if "method" in message and "id" in message:
                send({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": "Client method not supported by catalog capture"}})

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "tooldelta-fixture-capture", "version": "0.1.0"}}})
        initialized = receive(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, cursor, identifier = [], None, 2
        seen_cursors = set()
        while True:
            params = {} if cursor is None else {"cursor": cursor}
            send({"jsonrpc": "2.0", "id": identifier, "method": "tools/list", "params": params})
            page = receive(identifier)
            tools.extend(page["tools"])
            cursor = page.get("nextCursor")
            if cursor is None:
                break
            if cursor in seen_cursors or len(seen_cursors) > 100:
                raise RuntimeError("Repeated or excessive pagination cursor.")
            seen_cursors.add(cursor)
            identifier += 1
        return {"tools": tools, "capture": {"protocolVersion": initialized.get("protocolVersion"), "serverInfo": initialized.get("serverInfo")}}
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("Specify a trusted server command after --.")
    result = capture(command, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump({"tools": result["tools"]}, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"tools": len(result["tools"]), **result["capture"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
