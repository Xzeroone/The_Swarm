"""
The Swarm - Multi-Model Collaborative Agent System

A lightweight multi-model agent system that:
- Auto-downloads models based on task requirements
- Uses parallel voting for decisions
- Works offline with available models
- Prefers smallest model that can do the job
"""

from .config import MODEL_CATALOG, TASK_REQUIREMENTS, HARDWARE_PROFILES
from .hardware import HardwareDetector
from .registry import ModelRegistry
from .downloader import ModelDownloader
from .uninstaller import ModelUninstaller
from .selector import ModelSelector
from .voter import SwarmVoter
from .analyzer import TaskAnalyzer
from .orchestrator import SwarmOrchestrator

__all__ = [
    "MODEL_CATALOG",
    "TASK_REQUIREMENTS",
    "HARDWARE_PROFILES",
    "HardwareDetector",
    "ModelRegistry",
    "ModelDownloader",
    "ModelUninstaller",
    "ModelSelector",
    "SwarmVoter",
    "TaskAnalyzer",
    "SwarmOrchestrator",
]

__version__ = "2.0.0"
