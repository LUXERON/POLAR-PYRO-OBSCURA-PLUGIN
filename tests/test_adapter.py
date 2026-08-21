import sys;from pathlib import Path;sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
import pytest
from adapter import PolicyError,admit_capability,admit_url,command
def resolver(address): return lambda *_args,**_kwargs:[(2,1,6,"",(address,443))]
def test_command_never_enables_private_or_file_access(): assert command()==("obscura","mcp")
def test_ssrf_destinations_fail_closed():
    for address in ("127.0.0.1","169.254.169.254","10.0.0.1"):
        with pytest.raises(PolicyError): admit_url("https://example.com",resolver=resolver(address))
def test_public_destination_and_declared_capability_pass(): assert admit_url("https://example.com/a",resolver=resolver("93.184.216.34"))=="https://example.com/a";assert admit_capability("browser.snapshot")=="browser.snapshot"
def test_undeclared_cookie_tool_rejected():
    with pytest.raises(PolicyError): admit_capability("browser.cookies")
