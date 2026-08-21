# Polar Pyro Obscura Plugin

Governed adapter between Polar Pyro and [Obscura](https://github.com/h4ckf0r0day/obscura), pinned at `5465ff76abde560c7e9d69b1ca85895562de38e4`. Obscura is the low-footprint headless execution backend in the browser capability family; this adapter prevents its broad MCP surface from becoming broad model authority.

## North star

Autonomous app-development sessions can obtain DOM snapshots, screenshots, console and network evidence without launching a personal browser, leaking credentials, pivoting into local/private networks, or allowing page content to select tools.

The adapter exposes only `browser.snapshot`, constructs the upstream-documented shell-free `obscura mcp` stdio command, omits Obscura's private-network and file-access flags, resolves destinations before admission, and rejects non-global IPs. Navigation is an internal adapter step after URL admission, not a model-facing capability. Cookies, storage state, interactive actions, JavaScript evaluation, network logs, console logs, PDFs, and screenshots are outside the promoted capability set. All page content remains untrusted evidence and requires the Sovereign Retrieval Oracle or browser/domain oracle before promotion.

```text
BrowserIntentIR → Polar broker → URL/SSRF policy → Obscura MCP
→ normalized snapshot receipt → oracle → PASS | FAIL | NO_RESULT
```

Run `py -m pytest -q`.

## Live qualification — 2026-08-21

The pinned Windows debug binary built from upstream commit `5465ff76abde560c7e9d69b1ca85895562de38e4` completed a shell-free MCP stdio handshake using protocol `2024-11-05`. It exposed 35 tools, navigated to the policy-admitted public fixture `https://example.com/`, and returned a 319-character DOM snapshot. The executable digest is `019dfa27032440257839afd82ec02bcc377f982c74d27127e9fc5a620d32f46d`; tool-catalog digest `66b1e3195c6609aa16e9c8dcb9044630416a131384900aea908e9dbe7b7cec20`; snapshot digest `7913c7caa69abc44d7bcc3fdb331e751ebea2195cbabad99ad8ce181ece632de`.

The low-footprint build omits Obscura's optional render feature, so screenshot/PDF capability is absent and remains unpromoted. Redirect/DNS-rebinding defenses, OS resource limits, process sandboxing, poison-page gauntlets, crash recovery, and signed broker receipts remain production gates. The adapter is MIT; Obscura remains Apache-2.0 and is not vendored here. See [WHITEPAPER.md](WHITEPAPER.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
