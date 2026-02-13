"""
Task Analyzer - Analyze tasks using tiny model to determine requirements
"""

import ollama
import re
import json
from typing import Dict


class TaskAnalyzer:
    ANALYZER_MODEL = "qwen2.5:0.5b"

    def __init__(self, config):
        self.config = config

    def analyze(self, goal: str) -> Dict:
        """
        Analyze task to determine model requirements.
        Uses tiny model for fast classification.
        """
        prompt = f"""Analyze this coding task. Reply with ONLY a JSON object.

Task: "{goal}"

Required format (NO other text):
{{"type":"code","complexity":"simple","needs_reasoning":false}}

Rules:
- type: code, debug, test, review, or general
- complexity: simple, medium, or complex  
- needs_reasoning: true or false

JSON only:"""

        try:
            response = ollama.chat(
                model=self.ANALYZER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"num_predict": 50, "temperature": 0.1},
            )

            content = response["message"]["content"]

            json_match = re.search(r"\{[^}]+\}", content)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {
            "type": "code",
            "complexity": self._estimate_complexity(goal),
            "needs_reasoning": True,
        }

    def _estimate_complexity(self, goal: str) -> str:
        """Quick complexity estimation based on keywords."""
        goal_lower = goal.lower()

        complex_keywords = [
            "algorithm",
            "optimize",
            "architecture",
            "system",
            "multiple",
            "integrate",
            "api",
            "database",
            "complex",
        ]
        simple_keywords = ["simple", "basic", "hello", "add", "print", "return"]

        for kw in complex_keywords:
            if kw in goal_lower:
                return "complex"

        for kw in simple_keywords:
            if kw in goal_lower:
                return "simple"

        return "medium"

    def classify_complexity(self, goal: str) -> str:
        """Quick complexity check."""
        result = self.analyze(goal)
        return result.get("complexity", "medium")

    def classify_type(self, goal: str) -> str:
        """Quick type classification."""
        result = self.analyze(goal)
        return result.get("type", "code")
