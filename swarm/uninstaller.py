"""
Model Uninstaller - Remove unused models to free space
"""

import subprocess
import shutil
from typing import List


class ModelUninstaller:
    def __init__(self, registry, config):
        self.registry = registry
        self.config = config

    def cleanup_unused(self, keep_models: List[str] = None) -> int:
        """
        Remove least-used models downloaded by swarm.

        Args:
            keep_models: Models that must not be removed

        Returns:
            Number of models removed
        """
        keep_models = keep_models or []
        removed = 0

        swarm_models = list(self.registry._registry.get("downloaded_by_swarm", []))

        for model in swarm_models:
            if model in keep_models:
                continue

            if self._should_remove(model):
                if self._uninstall(model):
                    self.registry._registry["downloaded_by_swarm"].remove(model)
                    self.registry._save()
                    removed += 1

        return removed

    def _should_remove(self, model: str) -> bool:
        """Check if model should be removed."""
        info = self.config.MODEL_CATALOG.get(model)
        if not info:
            return True

        if info.get("always_keep", False):
            return False

        usage = self.registry.get_usage_count(model)
        return usage < 3

    def _uninstall(self, model: str) -> bool:
        """Uninstall a model via ollama rm."""
        print(f"🗑️ Removing unused model: {model}")

        try:
            result = subprocess.run(
                ["ollama", "rm", model], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print(f"✅ Removed {model}")
                return True
            else:
                return False
        except Exception:
            return False

    def free_space_for(self, required_mb: int) -> bool:
        """
        Free enough space for a new model.

        Returns:
            True if enough space freed
        """
        free_gb = shutil.disk_usage("/").free / (1024**3)

        if free_gb * 1024 > required_mb + 500:
            return True

        while free_gb * 1024 < required_mb + 500:
            least_used = self.registry.get_least_used()
            if not least_used:
                return False

            if not self._uninstall(least_used):
                return False

            self.registry._registry["downloaded_by_swarm"].remove(least_used)
            self.registry._save()
            free_gb = shutil.disk_usage("/").free / (1024**3)

        return True
