"""
Swarm CLI - Command-line interface for config and model management.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Handle both package and direct imports
try:
    from .config_default import (
        load_config,
        save_config,
        show_config,
        get_recommended_model,
        detect_hardware_profile,
    )
except ImportError:
    from config_default import (
        load_config,
        save_config,
        show_config,
        get_recommended_model,
        detect_hardware_profile,
    )

CONFIG_DIR = Path.home() / ".swarm-config"


def cmd_config(args):
    """Handle config commands."""
    if args.set_key and args.set_value:
        config = load_config()

        # Parse value type
        value = args.set_value
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "").isdigit():
            value = float(value)

        config[args.set_key] = value
        save_config(config)
        print(f"✓ Set {args.set_key} = {value}")

    elif args.edit:
        editor = subprocess.run(["which", "nano", "vim", "vi"], capture_output=True)
        editor_cmd = editor.stdout.decode().strip().split("\n")[0] or "nano"
        config_file = CONFIG_DIR / "config.json"
        subprocess.run([editor_cmd, str(config_file)])

    else:
        print(show_config())


def cmd_models(args):
    """Handle models commands."""
    if args.download:
        print(f"📥 Downloading {args.download}...")
        result = subprocess.run(["ollama", "pull", args.download], capture_output=False)
        if result.returncode == 0:
            print(f"✓ Downloaded {args.download}")

    elif args.cleanup:
        print("🗑️ Cleaning up unused models...")
        config = load_config()
        keep_models = [
            config.get("default_model"),
            config.get("router_model"),
        ]
        keep_models = [m for m in keep_models if m]

        registry_file = Path.home() / ".swarm" / "model_registry.json"
        if registry_file.exists():
            try:
                registry = json.loads(registry_file.read_text())
                for model in registry.get("downloaded_by_swarm", []):
                    if model not in keep_models:
                        print(f"  Removing: {model}")
                        subprocess.run(["ollama", "rm", model], capture_output=True)
            except Exception as e:
                print(f"  Error: {e}")

        print("✓ Cleanup complete")

    elif args.recommend:
        profile = detect_hardware_profile()
        recommended = get_recommended_model(profile)
        print(f"Hardware profile: {profile}")
        print(f"Recommended model: {recommended}")

    else:
        print("Installed models:")
        print()
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n")[1:]:
                if line.strip():
                    parts = line.split()
                    model = parts[0]
                    size = parts[2] if len(parts) > 2 else "?"
                    print(f"  • {model} ({size})")

        print()
        config = load_config()
        print("Configured models:")
        print(f"  Default: {config.get('default_model')}")
        print(f"  Router: {config.get('router_model')}")


def cmd_hardware(args):
    """Show hardware info."""
    import psutil

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    print("Hardware Info:")
    print(f"  RAM: {ram.total / (1024**3):.1f}GB total")
    print(f"       {ram.available / (1024**3):.1f}GB available")
    print(f"  CPU cores: {psutil.cpu_count()}")
    print(f"  Free disk: {disk.free / (1024**3):.1f}GB")

    profile = detect_hardware_profile()
    recommended = get_recommended_model(profile)

    print()
    print(f"Detected profile: {profile}")
    print(f"Recommended model: {recommended}")


def cmd_update(args):
    """Update The Swarm."""
    swarm_dir = Path.home() / ".swarm"

    print("🔄 Updating The Swarm...")

    result = subprocess.run(
        ["git", "pull"], cwd=swarm_dir, capture_output=True, text=True
    )

    if "Already up to date" in result.stdout:
        print("✓ Already up to date")
    else:
        print(result.stdout)

    # Update dependencies
    venv_python = swarm_dir / "venv" / "bin" / "pip"
    if venv_python.exists():
        subprocess.run(
            [str(venv_python), "install", "-q", "-r", "requirements.txt"], cwd=swarm_dir
        )
        print("✓ Dependencies updated")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for swarm CLI."""
    parser = argparse.ArgumentParser(
        prog="swarm", description="The Swarm - Multi-Model Collaborative Agent"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # config subcommand
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("set_key", nargs="?", help="Config key to set")
    config_parser.add_argument("set_value", nargs="?", help="Value to set")
    config_parser.add_argument(
        "--edit", "-e", action="store_true", help="Open in editor"
    )
    config_parser.set_defaults(func=cmd_config)

    # models subcommand
    models_parser = subparsers.add_parser("models", help="Manage models")
    models_parser.add_argument(
        "--download", "-d", metavar="MODEL", help="Download a model"
    )
    models_parser.add_argument(
        "--cleanup", "-c", action="store_true", help="Remove unused models"
    )
    models_parser.add_argument(
        "--recommend", "-r", action="store_true", help="Show recommended model"
    )
    models_parser.set_defaults(func=cmd_models)

    # hardware subcommand
    hardware_parser = subparsers.add_parser("hardware", help="Show hardware info")
    hardware_parser.set_defaults(func=cmd_hardware)

    # update subcommand
    update_parser = subparsers.add_parser("update", help="Update The Swarm")
    update_parser.set_defaults(func=cmd_update)

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
