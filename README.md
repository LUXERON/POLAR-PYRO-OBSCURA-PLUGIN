# Polar Pyro Obscura Plugin

Governed adapter between Polar Pyro and [Obscura](https://github.com/h4ckf0r0day/obscura), pinned at `5465ff76abde560c7e9d69b1ca85895562de38e4`. Obscura is the low-footprint headless execution backend in the browser capability family; this adapter prevents its broad MCP surface from becoming broad model authority.

## North star

Autonomous app-development sessions can obtain DOM snapshots, screenshots, console and network evidence without launching a personal browser, leaking credentials, pivoting into local/private networks, or allowing page content to select tools.

The adapter exposes a closed allowlist, constructs the upstream-documented shell-free `obscura mcp` stdio command, omits Obscura's private-network and file-access flags, resolves destinations before admission, and rejects non-global IPs. Cookies and storage state are deliberately outside the default capability set. All page content remains untrusted evidence and requires the Sovereign Retrieval Oracle or browser/domain oracle before promotion.

```text
BrowserIntentIR → Polar broker → URL/SSRF policy → Obscura MCP
→ normalized snapshot receipt → oracle → PASS | FAIL | NO_RESULT
```

Run `py -m pytest -q`. Production gates still include redirect/DNS-rebinding defenses, resource limits, process sandboxing, exact binary/SBOM verification, MCP handshake qualification, poison pages, crash recovery and signed receipts. The adapter is MIT; Obscura remains Apache-2.0 and is not vendored here. See [WHITEPAPER.md](WHITEPAPER.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
