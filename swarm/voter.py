"""
Swarm Voter - Parallel voting with multiple tiny models
"""

import ollama
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from collections import Counter
import re


class SwarmVoter:
    def __init__(self, config, selector):
        self.config = config
        self.selector = selector

    def vote(
        self, prompt: str, voter_models: List[str] = None, timeout: float = 10.0
    ) -> Dict:
        """
        Run parallel vote across multiple models.

        Returns:
            {
                "action": "plan_skill",
                "confidence": 0.67,
                "votes": {"plan_skill": 2, "test_skill": 1},
                "responses": [...]
            }
        """
        if voter_models is None:
            voter_models = self.selector.select_voters(3)

        responses = []

        try:
            with ThreadPoolExecutor(max_workers=len(voter_models)) as executor:
                futures = {
                    executor.submit(self._call_voter, model, prompt, timeout): model
                    for model in voter_models
                }

                for future in as_completed(futures, timeout=timeout + 10):
                    model = futures[future]
                    try:
                        result = future.result(timeout=timeout)
                        responses.append(
                            {
                                "model": model,
                                "response": result,
                            }
                        )
                    except Exception as e:
                        pass
        except TimeoutError:
            pass

        if not responses:
            action = self.quick_vote(prompt)
            return {
                "action": action,
                "confidence": 0.5,
                "votes": {action: 1},
                "responses": [],
            }

        return self._tally_votes(responses)

    def _call_voter(self, model: str, prompt: str, timeout: float) -> str:
        """Call a single voter model."""
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_predict": 20,
                "temperature": 0.3,
            },
        )
        return response["message"]["content"]

    def _tally_votes(self, responses: List[Dict]) -> Dict:
        """Count votes and determine winner."""
        actions = []
        for r in responses:
            action = self._parse_action(r["response"])
            actions.append(action)

        if not actions:
            return {
                "action": "plan_skill",
                "confidence": 0.0,
                "votes": {},
                "responses": responses,
            }

        vote_counts = Counter(actions)
        winner, count = vote_counts.most_common(1)[0]
        confidence = count / len(actions)

        return {
            "action": winner,
            "confidence": confidence,
            "votes": dict(vote_counts),
            "responses": responses,
        }

    def _parse_action(self, response: str) -> str:
        """Extract action from voter response."""
        response = response.lower().strip()

        actions = [
            "plan_skill",
            "write_skill",
            "test_skill",
            "analyze_results",
            "complete",
            "failed",
            "direct_answer",
            "retry_plan",
        ]

        for action in actions:
            if action.replace("_", " ") in response or action in response:
                return action

        return "plan_skill"

    def quick_vote(self, prompt: str) -> str:
        """Fast single-model vote for simple decisions."""
        model = self.selector.select_router()

        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 10, "temperature": 0.1},
        )

        return self._parse_action(response["message"]["content"])
