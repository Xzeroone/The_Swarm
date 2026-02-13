"""
Hardware Detection - Detect system capabilities and select profile
"""

import psutil
import shutil
from typing import Dict


class HardwareDetector:
    def detect(self) -> Dict:
        """Detect system capabilities."""
        ram = psutil.virtual_memory()
        disk = shutil.disk_usage("/")

        return {
            "total_ram_gb": ram.total / (1024**3),
            "available_ram_gb": ram.available / (1024**3),
            "free_disk_gb": disk.free / (1024**3),
            "cpu_cores": psutil.cpu_count(),
            "max_parallel_models": self._estimate_parallel_capacity(ram.available),
        }

    def _estimate_parallel_capacity(self, available_bytes: int) -> int:
        """Estimate how many models can run in parallel."""
        available_mb = available_bytes / (1024**2)
        if available_mb > 8000:
            return 3
        elif available_mb > 4000:
            return 2
        else:
            return 1

    def get_profile(self) -> str:
        """Select hardware profile based on RAM."""
        hw = self.detect()
        ram = hw["total_ram_gb"]

        if ram < 6:
            return "minimal"
        elif ram < 12:
            return "limited"
        elif ram < 24:
            return "moderate"
        else:
            return "powerful"

    def can_fit_model(self, model_info: Dict) -> bool:
        """Check if model fits in available RAM."""
        available = psutil.virtual_memory().available / (1024 * 1024)
        return model_info["ram_mb"] < available * 0.7

    def get_max_tier(self) -> int:
        """Get max model tier for current hardware."""
        from .config import HARDWARE_PROFILES

        profile = HARDWARE_PROFILES.get(self.get_profile(), {})
        return profile.get("max_model_tier", 1)

    def allow_parallel(self) -> bool:
        """Check if parallel execution is allowed."""
        from .config import HARDWARE_PROFILES

        profile = HARDWARE_PROFILES.get(self.get_profile(), {})
        return profile.get("allow_parallel", False)
