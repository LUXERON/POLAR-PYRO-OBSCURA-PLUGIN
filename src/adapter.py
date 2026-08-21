"""Fail-closed policy and shell-free command construction for Obscura MCP."""
from __future__ import annotations
from dataclasses import dataclass
import ipaddress
import socket
from urllib.parse import urlparse

UPSTREAM_COMMIT="5465ff76abde560c7e9d69b1ca85895562de38e4"
ALLOWED_CAPABILITIES=frozenset({"browser.snapshot"})

class PolicyError(ValueError): pass

def command(executable:str="obscura")->tuple[str,...]:
    if not executable or "\n" in executable or "\r" in executable: raise PolicyError("invalid executable")
    # Deliberately omit --allow-private-network and --allow-file-access.
    return (executable,"mcp")

def admit_url(value:str, *, resolver=socket.getaddrinfo)->str:
    url=urlparse(value)
    if url.scheme not in {"http","https"} or not url.hostname or url.username or url.password: raise PolicyError("URL must be credential-free HTTP(S)")
    addresses={row[4][0] for row in resolver(url.hostname,url.port or (443 if url.scheme=="https" else 80),type=socket.SOCK_STREAM)}
    if not addresses: raise PolicyError("hostname did not resolve")
    for raw in addresses:
        ip=ipaddress.ip_address(raw.split("%")[0])
        if not ip.is_global: raise PolicyError("private, loopback, link-local and metadata destinations are denied")
    return url.geturl()

def admit_capability(name:str)->str:
    if name not in ALLOWED_CAPABILITIES: raise PolicyError("capability is not declared")
    return name
