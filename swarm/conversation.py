"""
Conversation manager for follow-up questions.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ConversationManager:
    """Manages conversation history for chat mode."""

    def __init__(self, config_dir: Path = None, max_history: int = 20):
        if config_dir is None:
            config_dir = Path.home() / ".swarm-config"

        self.history_file = config_dir / "conversation_history.json"
        self.max_history = max_history
        self._history: List[Dict] = []
        self._load()

    def _load(self):
        """Load history from file."""
        if self.history_file.exists():
            try:
                self._history = json.loads(self.history_file.read_text())
            except (json.JSONDecodeError, KeyError):
                self._history = []
        else:
            self._history = []

    def _save(self):
        """Save history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(
            json.dumps(self._history[-self.max_history :], indent=2)
        )

    def add(self, role: str, content: str):
        """Add a message to history."""
        self._history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        self._save()

    def get_messages(self, include_system: bool = False) -> List[Dict]:
        """Get messages in ollama format."""
        messages = []

        if include_system:
            messages.append(
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Be concise and helpful.",
                }
            )

        for h in self._history:
            messages.append({"role": h["role"], "content": h["content"]})

        return messages

    def clear(self):
        """Clear conversation history."""
        self._history = []
        self._save()

    def get_last_n(self, n: int) -> List[Dict]:
        """Get last n messages."""
        return self._history[-n:] if self._history else []

    def __len__(self):
        return len(self._history)

    def __repr__(self):
        return f"ConversationManager(messages={len(self._history)})"
