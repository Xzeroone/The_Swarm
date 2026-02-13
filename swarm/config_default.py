"""
Default configuration and hardware auto-detection for The Swarm.
"""

import json
import psutil
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path.home() / ".swarm-config"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "version": "2.0.0",
    "default_model": "auto",
    "router_model": "qwen2.5:0.5b",
    "voter_models": ["qwen2.5:0.5b", "tinyllama", "phi3:mini"],
    "offline_mode": False,
    "max_iterations": 12,
    "workspace": str(CONFIG_DIR / "workspace"),
    "auto_cleanup": True,
    "auto_download": True,
    "hardware_profile": "moderate",
    "ram_gb": 8,
}

MODEL_RECOMMENDATIONS = {
    "minimal": {
        "default_model": "qwen2.5-coder:1.5b",
        "max_tier": 1,
        "allow_parallel": False,
    },
    "limited": {
        "default_model": "qwen2.5-coder:1.5b",
        "max_tier": 2,
        "allow_parallel": False,
    },
    "moderate": {
        "default_model": "qwen2.5-coder:3b",
        "max_tier": 2,
        "allow_parallel": True,
    },
    "powerful": {
        "default_model": "qwen2.5-coder:3b",
        "max_tier": 2,
        "allow_parallel": True,
    },
}


def detect_hardware_profile() -> str:
    """Detect hardware profile based on available RAM."""
    ram_gb = psutil.virtual_memory().total / (1024**3)

    if ram_gb >= 24:
        return "powerful"
    elif ram_gb >= 12:
        return "moderate"
    elif ram_gb >= 6:
        return "limited"
    else:
        return "minimal"


def get_recommended_model(profile: str = None) -> str:
    """Get recommended default model for hardware profile."""
    if profile is None:
        profile = detect_hardware_profile()

    return MODEL_RECOMMENDATIONS.get(profile, {}).get(
        "default_model", "qwen2.5-coder:1.5b"
    )


def create_default_config() -> Dict[str, Any]:
    """Create default config with auto-detected values."""
    profile = detect_hardware_profile()
    ram_gb = int(psutil.virtual_memory().total / (1024**3))

    config = DEFAULT_CONFIG.copy()
    config["hardware_profile"] = profile
    config["ram_gb"] = ram_gb
    config["default_model"] = get_recommended_model(profile)
    config["workspace"] = str(CONFIG_DIR / "workspace")

    return config


def load_config() -> Dict[str, Any]:
    """Load config from file, creating default if not exists."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)

            # Resolve "auto" for default_model
            if config.get("default_model") == "auto":
                config["default_model"] = get_recommended_model(
                    config.get("hardware_profile")
                )

            return config
        except (json.JSONDecodeError, KeyError):
            pass

    # Create default config
    config = create_default_config()
    save_config(config)
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save config to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific config value."""
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set a specific config value."""
    config = load_config()
    config[key] = value
    save_config(config)


def show_config() -> str:
    """Return formatted config."""
    config = load_config()
    return json.dumps(config, indent=2)
