"""
Model Selector - Select best model for task (smallest that can do the job)
"""

from typing import Dict, List, Optional
from .config import (
    MODEL_CATALOG,
    TASK_REQUIREMENTS,
    DEFAULT_CODER_MODEL,
    DEFAULT_ROUTER_MODEL,
)


class ModelSelector:
    def __init__(self, config, registry, downloader, hardware):
        self.config = config
        self.registry = registry
        self.downloader = downloader
        self.hardware = hardware

    def select_for_task(
        self, task_type: str, complexity: str = "medium", offline: bool = False
    ) -> Optional[str]:
        """
        Select smallest model that can do the job.

        Priority:
        1. Smallest installed model that meets requirements
        2. Download smallest that meets requirements (if not offline)
        3. Fall back to best available
        """
        requirements = TASK_REQUIREMENTS.get(task_type, {})
        min_tier = requirements.get("min_tier", 0)
        min_caps = requirements.get("min_capabilities", [])

        if complexity in requirements.get("complexity_upgrade", {}):
            min_tier = requirements["complexity_upgrade"][complexity]

        max_tier = min(self.hardware.get_max_tier(), 2)

        candidates = self._get_candidates(min_tier, min_caps, max_tier)

        installed = self.registry.get_installed_models()
        for model in candidates:
            if model in installed:
                info = MODEL_CATALOG.get(model, {})
                if self.hardware.can_fit_model(info):
                    self.registry.record_usage(model)
                    return model

        if not offline:
            for model in candidates:
                info = MODEL_CATALOG.get(model, {})
                if self.hardware.can_fit_model(info):
                    if self.downloader.ensure_available(model):
                        self.registry.record_usage(model)
                        return model

        for model in installed:
            if model in MODEL_CATALOG:
                return model

        return DEFAULT_ROUTER_MODEL

    def _get_candidates(
        self, min_tier: int, min_caps: List[str], max_tier: int
    ) -> List[str]:
        """Get candidate models sorted by size (smallest first)."""
        candidates = []

        for model, info in MODEL_CATALOG.items():
            tier = info.get("tier", 99)
            if tier < min_tier or tier > max_tier:
                continue

            model_caps = info.get("capabilities", [])
            if not all(cap in model_caps for cap in min_caps):
                continue

            candidates.append((model, info["size_mb"]))

        candidates.sort(key=lambda x: x[1])
        return [model for model, _ in candidates]

    def select_coder(self, complexity: str = "medium", offline: bool = False) -> str:
        """Select model for code generation."""
        return self.select_for_task("code_generation", complexity, offline)

    def select_router(self, offline: bool = False) -> str:
        """Select model for routing decisions."""
        return self.select_for_task("routing", "simple", offline)

    def select_voters(self, count: int = 3, offline: bool = False) -> List[str]:
        """Select models for voting."""
        candidates = self._get_candidates(
            min_tier=0, min_caps=["voting"], max_tier=self.hardware.get_max_tier()
        )

        selected = []
        for model in candidates[:count]:
            if self.downloader.ensure_available(model, auto_download=not offline):
                selected.append(model)

        if not selected:
            selected = [DEFAULT_ROUTER_MODEL]

        return selected
