#!/usr/bin/env python3
"""Resolve environment variables into nanobot config and launch gateway."""

import json
import os
import sys
from pathlib import Path

def resolve_config():
    """Read config.json, inject env vars, write resolved config."""
    config_path = Path(__file__).parent / "nanobot" / "config.json"
    workspace_path = Path(__file__).parent / "nanobot" / "workspace"
    resolved_path = Path(__file__).parent / "nanobot" / "config.resolved.json"
    
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Resolve LLM provider
    if "custom" in config.get("providers", {}):
        if api_key := os.environ.get("LLM_API_KEY"):
            config["providers"]["custom"]["apiKey"] = api_key
        if api_base := os.environ.get("LLM_API_BASE_URL"):
            config["providers"]["custom"]["apiBase"] = api_base
    
    # Resolve gateway
    if "gateway" in config:
        if host := os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
            config["gateway"]["host"] = host
        if port := os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT"):
            config["gateway"]["port"] = int(port)
    
    # Resolve webchat
    if "channels" in config and "webchat" in config["channels"]:
        if ws_url := os.environ.get("NANOBOT_WS_URL"):
            config["channels"]["webchat"]["wsUrl"] = ws_url
    
    # Resolve MCP
    if "tools" in config and "mcpServers" in config["tools"]:
        for server_name, server_config in config["tools"]["mcpServers"].items():
            if "env" in server_config:
                for env_key in server_config["env"]:
                    if env_value := os.environ.get(env_key):
                        server_config["env"][env_key] = env_value
    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)
    
    return str(resolved_path), str(workspace_path)

if __name__ == "__main__":
    resolved_config, workspace = resolve_config()
    
    # Use full path to nanobot in venv
    nanobot_path = "/app/.venv/bin/nanobot"
    os.execvp(nanobot_path, [nanobot_path, "gateway", "--config", resolved_config, "--workspace", workspace])
