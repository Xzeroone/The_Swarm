"""
Swarm Configuration - Model Catalog, Task Mapping, Hardware Profiles
"""

MODEL_CATALOG = {
    "qwen2.5:0.5b": {
        "size_mb": 397,
        "ram_mb": 500,
        "tier": 0,
        "capabilities": ["classification", "voting", "simple_code", "routing"],
        "speed_rating": 5,
        "code_quality": 2,
        "reasoning_quality": 2,
        "always_keep": True,
    },
    "tinyllama": {
        "size_mb": 637,
        "ram_mb": 800,
        "tier": 0,
        "capabilities": ["classification", "voting", "review", "routing"],
        "speed_rating": 5,
        "code_quality": 2,
        "reasoning_quality": 3,
        "always_keep": False,
    },
    "qwen2.5-coder:1.5b": {
        "size_mb": 986,
        "ram_mb": 1200,
        "tier": 1,
        "capabilities": ["code_generation", "debugging", "refactoring"],
        "speed_rating": 3,
        "code_quality": 4,
        "reasoning_quality": 3,
        "always_keep": False,
    },
    "qwen2.5-coder:3b": {
        "size_mb": 1900,
        "ram_mb": 2500,
        "tier": 2,
        "capabilities": ["complex_code", "architecture", "reasoning"],
        "speed_rating": 2,
        "code_quality": 4,
        "reasoning_quality": 4,
        "always_keep": False,
    },
    "phi3:mini": {
        "size_mb": 2200,
        "ram_mb": 2800,
        "tier": 2,
        "capabilities": ["reasoning", "review", "analysis"],
        "speed_rating": 2,
        "code_quality": 3,
        "reasoning_quality": 4,
        "always_keep": False,
    },
}

TASK_REQUIREMENTS = {
    "routing": {
        "min_capabilities": ["classification"],
        "min_tier": 0,
        "prefer_tier": 0,
    },
    "code_generation": {
        "min_capabilities": ["code_generation"],
        "min_tier": 1,
        "prefer_tier": 1,
        "complexity_upgrade": {
            "medium": 1,
            "complex": 2,
        },
    },
    "simple_code": {
        "min_capabilities": ["simple_code"],
        "min_tier": 0,
        "prefer_tier": 0,
    },
    "voting": {
        "min_capabilities": ["voting"],
        "min_tier": 0,
        "prefer_tier": 0,
        "voter_count": 3,
    },
    "review": {
        "min_capabilities": ["review"],
        "min_tier": 0,
        "prefer_tier": 0,
    },
    "debugging": {
        "min_capabilities": ["debugging"],
        "min_tier": 1,
        "prefer_tier": 1,
    },
}

HARDWARE_PROFILES = {
    "minimal": {
        "min_ram_gb": 4,
        "max_model_tier": 1,
        "allow_parallel": False,
        "max_loaded_models": 1,
    },
    "limited": {
        "min_ram_gb": 8,
        "max_model_tier": 2,
        "allow_parallel": False,
        "max_loaded_models": 1,
    },
    "moderate": {
        "min_ram_gb": 16,
        "max_model_tier": 2,
        "allow_parallel": True,
        "max_loaded_models": 3,
    },
    "powerful": {
        "min_ram_gb": 32,
        "max_model_tier": 2,
        "allow_parallel": True,
        "max_loaded_models": 5,
    },
}

VOTER_MODELS = ["qwen2.5:0.5b", "tinyllama", "phi3:mini"]

DEFAULT_CODER_MODEL = "qwen2.5-coder:1.5b"
DEFAULT_ROUTER_MODEL = "qwen2.5:0.5b"
