"""Live, shell-free qualification for the pinned Obscura MCP binary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import queue
import subprocess
import threading
import time

from adapter import admit_url


class QualificationError(RuntimeError):
    pass


class McpClient:
    def __init__(self, executable: Path) -> None:
        self.process = subprocess.Popen(
            [str(executable), "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            shell=False,
        )
        self.messages: queue.Queue[dict] = queue.Queue()
        self.stderr: list[str] = []
        threading.Thread(target=self._stdout, daemon=True).start()
        threading.Thread(target=self._stderr, daemon=True).start()
        self.next_id = 1

    def _stdout(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                self.messages.put(value)

    def _stderr(self) -> None:
        assert self.process.stderr is not None
        for line in self.process.stderr:
            self.stderr.append(line.rstrip())
            if len(self.stderr) > 100:
                del self.stderr[:25]

    def send(self, value: dict) -> None:
        if self.process.poll() is not None:
            raise QualificationError(f"Obscura exited {self.process.returncode}")
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(value, separators=(",", ":")) + "\n")
        self.process.stdin.flush()

    def request(self, method: str, params: dict, timeout: float = 30) -> dict:
        request_id = self.next_id
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                message = self.messages.get(timeout=min(0.2, max(0.01, deadline - time.monotonic())))
            except queue.Empty:
                if self.process.poll() is not None:
                    raise QualificationError(f"Obscura exited {self.process.returncode}: {' | '.join(self.stderr[-5:])}")
                continue
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise QualificationError(f"{method} failed: {message['error']}")
            result = message.get("result")
            if not isinstance(result, dict):
                raise QualificationError(f"{method} returned no object")
            return result
        raise QualificationError(f"{method} timed out")

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


def text_content(result: dict) -> str:
    return "\n".join(
        str(item.get("text", "")) for item in result.get("content", [])
        if isinstance(item, dict) and item.get("type") == "text"
    )


def qualify(executable: Path, url: str) -> dict:
    if not executable.is_file():
        raise QualificationError("Obscura executable does not exist")
    admitted = admit_url(url)
    binary_sha = hashlib.sha256(executable.read_bytes()).hexdigest()
    client = McpClient(executable)
    try:
        initialized = client.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "polar-pyro-obscura-qualifier", "version": "0.2.0"},
        })
        client.send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        listed = client.request("tools/list", {})
        names = sorted(str(item.get("name")) for item in listed.get("tools", []) if isinstance(item, dict))
        # The low-footprint build intentionally qualifies navigation and DOM
        # evidence without the optional render feature required for screenshots.
        required = {"browser_navigate", "browser_snapshot"}
        if not required.issubset(names):
            raise QualificationError(f"required tools missing: {sorted(required - set(names))}")
        navigation = client.request("tools/call", {"name": "browser_navigate", "arguments": {"url": admitted}}, timeout=45)
        if navigation.get("isError"):
            raise QualificationError("browser_navigate returned an error")
        snapshot = client.request("tools/call", {"name": "browser_snapshot", "arguments": {"max_chars": 12000}}, timeout=30)
        if snapshot.get("isError"):
            raise QualificationError("browser_snapshot returned an error")
        evidence = text_content(snapshot)
        if len(evidence.strip()) < 40:
            raise QualificationError("browser_snapshot evidence was empty or degenerate")
        return {
            "schema_version": "polar.obscura-qualification/v1",
            "status": "PASS",
            "upstream_commit": "5465ff76abde560c7e9d69b1ca85895562de38e4",
            "protocol_version": initialized.get("protocolVersion"),
            "server_info": initialized.get("serverInfo"),
            "admitted_url": admitted,
            "binary_sha256": binary_sha,
            "tool_count": len(names),
            "tool_catalog_sha256": hashlib.sha256(json.dumps(names, separators=(",", ":")).encode()).hexdigest(),
            "snapshot_characters": len(evidence),
            "snapshot_sha256": hashlib.sha256(evidence.encode()).hexdigest(),
        }
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--url", default="https://example.com/")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        receipt = qualify(args.executable.resolve(), args.url)
    except Exception as exc:
        receipt = {"schema_version": "polar.obscura-qualification/v1", "status": "NO_RESULT", "error": f"{type(exc).__name__}: {exc}"}
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
