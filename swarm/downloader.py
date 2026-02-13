"""
Model Downloader - Auto-download models via ollama pull
"""

import subprocess
import sys
import os
from typing import Dict, Optional, List


class ModelDownloader:
    def __init__(self, registry, config):
        self.registry = registry
        self.config = config
        self.auto_download = (
            os.environ.get("SWARM_AUTO_DOWNLOAD", "true").lower() == "true"
        )

    def ensure_available(self, model: str, auto_download: bool = None) -> bool:
        """
        Ensure model is available, downloading if needed.

        Returns:
            True if model is ready, False if couldn't get it
        """
        if auto_download is None:
            auto_download = self.auto_download

        if self.registry.is_installed(model):
            return True

        if not auto_download:
            return False

        info = self.config.MODEL_CATALOG.get(model)
        if not info:
            print(f"⚠️ Unknown model: {model}")
            return False

        return self._download(model, info)

    def _download(self, model: str, info: Dict) -> bool:
        """Download a model with progress."""
        size_mb = info["size_mb"]

        print(f"📥 Auto-downloading {model} (~{size_mb}MB)...")

        try:
            process = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"  {line}", file=sys.stderr)

            process.wait()

            if process.returncode == 0:
                print(f"✅ Downloaded {model}")
                self.registry.mark_downloaded_by_swarm(model)
                return True
            else:
                print(f"❌ Failed to download {model}")
                return False

        except Exception as e:
            print(f"❌ Download error: {e}")
            return False

    def download_with_fallback(
        self, preferred: str, fallbacks: List[str], auto_download: bool = None
    ) -> Optional[str]:
        """
        Try to download preferred, fall back to alternatives.
        Returns the model that was successfully downloaded.
        """
        if self.ensure_available(preferred, auto_download):
            return preferred

        for fallback in fallbacks:
            if self.ensure_available(fallback, auto_download):
                return fallback

        return None

    def download_voters(self, count: int = 3) -> List[str]:
        """Download voter models if needed."""
        from .config import VOTER_MODELS

        downloaded = []
        for model in VOTER_MODELS[:count]:
            if self.ensure_available(model):
                downloaded.append(model)

        return downloaded
