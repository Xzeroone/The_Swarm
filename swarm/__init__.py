"""
The Swarm - Multi-Model Collaborative Agent System

A lightweight multi-model agent system that:
- Auto-downloads models based on task requirements
- Uses parallel voting for decisions
- Works offline with available models
- Prefers smallest model that can do the job
- Auto-detects intent (chat vs task)
- Maintains conversation history
"""

from .config import MODEL_CATALOG, TASK_REQUIREMENTS, HARDWARE_PROFILES
from .config_default import (
    load_config,
    save_config,
    show_config,
    get_recommended_model,
    detect_hardware_profile,
    CONFIG_DIR,
    CONFIG_FILE,
)
from .hardware import HardwareDetector
from .registry import ModelRegistry
from .downloader import ModelDownloader
from .uninstaller import ModelUninstaller
from .selector import ModelSelector
from .voter import SwarmVoter
from .analyzer import TaskAnalyzer
from .orchestrator import SwarmOrchestrator
from .intent import classify_intent, classify_intent_with_model
from .conversation import ConversationManager

__all__ = [
    "MODEL_CATALOG",
    "TASK_REQUIREMENTS",
    "HARDWARE_PROFILES",
    "load_config",
    "save_config",
    "show_config",
    "get_recommended_model",
    "detect_hardware_profile",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "HardwareDetector",
    "ModelRegistry",
    "ModelDownloader",
    "ModelUninstaller",
    "ModelSelector",
    "SwarmVoter",
    "TaskAnalyzer",
    "SwarmOrchestrator",
    "classify_intent",
    "classify_intent_with_model",
    "ConversationManager",
]

__version__ = "2.1.0"
