import json
import shlex
import subprocess
from typing import List, Optional

from config import CONFIG


class MCPClient:
    def __init__(self, command: Optional[str] = None, args: Optional[str] = None):
        self.command = command or CONFIG.mcp_server_cmd
        self.args = args or CONFIG.mcp_server_args

    def list_tools(self) -> List[str]:
        if not self.command:
            return []
        cmd = [self.command] + (shlex.split(self.args) if self.args else [])
        # The exact contract depends on your MCP server; here we assume it supports a --list-tools json output
        try:
            result = subprocess.run(cmd + ["--list-tools"], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            tools = [tool.get("name", "") for tool in data.get("tools", [])]
            return tools
        except Exception:
            return []