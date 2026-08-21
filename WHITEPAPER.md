# Lightweight Browsing Without Ambient Authority

Obscura supplies an unusually useful execution substrate: a native headless browser and MCP/CDP-compatible surface without requiring the host IDE to own a full browser runtime. Polar Pyro assigns it one role—bounded browser execution—and places policy above it.

The model never sees the raw executable, flags, environment or full runtime tool list. A closed intent is resolved against the pinned manifest. The adapter denies local files and non-global networks, starts the process without a shell, normalizes results to evidence, and gives authorization decisions to the host. This separation allows Obscura to evolve or be replaced without changing the Browser UI or oracle.

The system is successful when adversarial pages cannot alter routing or grants, SSRF/rebinding controls hold, personal state is absent, snapshots are reproducible and cited, and backend failure becomes `NO_RESULT` rather than a fabricated success.
