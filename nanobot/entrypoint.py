"""Resolve environment variables into config.json and start nanobot gateway."""
import json
import os
import re


def resolve_env_vars(config: dict) -> dict:
    def resolve_value(value):
        if isinstance(value, str):
            if value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                return os.environ.get(var_name, "")
            match = re.match(r'\$\{([^}:]+)(?::-([^}]*))?\}', value)
            if match:
                var_name = match.group(1)
                default = match.group(2) or ""
                return os.environ.get(var_name, default)
        elif isinstance(value, dict):
            return {k: resolve_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(item) for item in value]
        return value
    return resolve_value(config)


def main():
    with open("./config.json") as f:
        config = json.load(f)
    config = resolve_env_vars(config)
    config.setdefault("channels", {})
    config["channels"]["webchat"] = {
        "enabled": True,
        "host": os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0"),
        "port": int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765")),
        "accessKey": os.environ.get("NANOBOT_ACCESS_KEY", ""),
        "allow_from": ["*"]
    }
    with open("./config.resolved.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"Starting nanobot gateway with config: {config}")
    os.execvp("nanobot", ["nanobot", "gateway", "--config", "./config.resolved.json", "--workspace", "./workspace"])


if __name__ == "__main__":
    main()
