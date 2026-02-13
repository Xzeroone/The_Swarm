"""
Model Registry - Track which models are installed and their metadata
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional


class ModelRegistry:
    REGISTRY_FILE = Path.home() / ".swarm" / "model_registry.json"

    def __init__(self):
        self.REGISTRY_FILE.parent.mkdir(exist_ok=True)
        self._registry = self._load()

    def _load(self) -> Dict:
        """Load registry from disk."""
        if self.REGISTRY_FILE.exists():
            try:
                return json.loads(self.REGISTRY_FILE.read_text())
            except json.JSONDecodeError:
                pass
        return {"installed": {}, "downloaded_by_swarm": [], "usage": {}}

    def _save(self):
        """Save registry to disk."""
        self.REGISTRY_FILE.write_text(json.dumps(self._registry, indent=2))

    def get_installed_models(self) -> List[str]:
        """Get list of installed ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                return []

            models = []
            for line in result.stdout.strip().split("\n")[1:]:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)

            return models
        except Exception:
            return []

    def is_installed(self, model: str) -> bool:
        """Check if a model is installed (handles model:tag format)."""
        installed = self.get_installed_models()
        # Direct match
        if model in installed:
            return True
        # Prefix match (model vs model:latest)
        model_base = model.split(":")[0]
        for installed_model in installed:
            installed_base = installed_model.split(":")[0]
            if model_base == installed_base:
                return True
        return False

    def mark_downloaded_by_swarm(self, model: str):
        """Mark a model as downloaded by swarm (for cleanup)."""
        if model not in self._registry["downloaded_by_swarm"]:
            self._registry["downloaded_by_swarm"].append(model)
            self._save()

    def is_swarm_downloaded(self, model: str) -> bool:
        """Check if swarm downloaded this model."""
        return model in self._registry.get("downloaded_by_swarm", [])

    def record_usage(self, model: str):
        """Record that a model was used (for cleanup decisions)."""
        if "usage" not in self._registry:
            self._registry["usage"] = {}

        self._registry["usage"][model] = self._registry["usage"].get(model, 0) + 1
        self._save()

    def get_usage_count(self, model: str) -> int:
        """Get usage count for a model."""
        return self._registry.get("usage", {}).get(model, 0)

    def get_least_used(self, exclude: List[str] = None) -> Optional[str]:
        """Get least-used swarm-downloaded model."""
        exclude = exclude or []
        swarm_models = self._registry.get("downloaded_by_swarm", [])
        usage = self._registry.get("usage", {})

        candidates = [m for m in swarm_models if m not in exclude]

        if not candidates:
            return None

        return min(candidates, key=lambda m: usage.get(m, 0))
