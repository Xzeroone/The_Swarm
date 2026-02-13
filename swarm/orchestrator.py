"""
Swarm Orchestrator - Main coordinator for multi-model collaboration
"""

import ollama
from typing import Dict, Optional, List
from pathlib import Path
import subprocess
import tempfile
import os

from .intent import classify_intent
from .conversation import ConversationManager


class SwarmOrchestrator:
    MAX_ITERATIONS = 12

    def __init__(
        self,
        config,
        hardware,
        registry,
        downloader,
        uninstaller,
        selector,
        voter,
        analyzer,
    ):
        self.config = config
        self.hardware = hardware
        self.registry = registry
        self.downloader = downloader
        self.uninstaller = uninstaller
        self.selector = selector
        self.voter = voter
        self.analyzer = analyzer
        self.conversation = ConversationManager()

    def run(self, goal: str, offline: bool = False, force_mode: str = None) -> Dict:
        """
        Run the swarm on a goal.

        Args:
            goal: The task to accomplish or question to answer
            offline: If True, don't download new models
            force_mode: "task" or "chat" to override auto-detection

        Returns:
            {"success": bool, "result": str, "iterations": int, "type": str}
        """
        # Determine intent
        if force_mode:
            intent = force_mode
        else:
            intent = classify_intent(goal)

        if intent == "chat":
            return self._chat(goal, offline)

        # Task mode
        profile = self.hardware.get_profile()
        print(f"🖥️ Hardware profile: {profile}")

        task_info = self.analyzer.analyze(goal)
        print(f"📋 Task: {task_info['type']}, complexity: {task_info['complexity']}")

        coder_model = self.selector.select_coder(
            task_info["complexity"], offline=offline
        )

        if not coder_model:
            return {
                "success": False,
                "error": "No suitable model available",
                "iterations": 0,
                "type": "task",
            }

        print(f"🤖 Using coder model: {coder_model}")

        return self._run_loop(goal, coder_model, task_info, offline)

    def _chat(self, question: str, offline: bool) -> Dict:
        """Answer question directly with conversation history."""
        model = self.selector.select_router(offline=offline)

        print(f"💬 Chat mode (using {model})")
        print()

        # Add user message to history
        self.conversation.add("user", question)

        # Get messages for context
        messages = self.conversation.get_messages(include_system=True)

        try:
            response = ollama.chat(
                model=model, messages=messages, options={"temperature": 0.7}
            )

            answer = response["message"]["content"]

            # Add assistant response to history
            self.conversation.add("assistant", answer)

            print(answer)

            return {
                "success": True,
                "type": "chat",
                "response": answer,
                "iterations": 1,
            }
        except Exception as e:
            return {"success": False, "type": "chat", "error": str(e), "iterations": 0}

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation.clear()
        print("✓ Conversation history cleared")

    def _run_loop(
        self, goal: str, coder_model: str, task_info: Dict, offline: bool
    ) -> Dict:
        """Main swarm execution loop."""
        iteration = 0
        history = []
        skill_code = ""

        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}/{self.MAX_ITERATIONS}")

            # Check if last test passed - force complete
            if history:
                last_action = history[-1]
                if last_action["action"] == "test_skill" and last_action.get(
                    "result", {}
                ).get("success"):
                    print("✅ Test passed, completing...")
                    return {
                        "success": True,
                        "result": skill_code,
                        "iterations": iteration,
                    }

            decision = self._vote_on_action(goal, iteration, history, skill_code)

            action = decision["action"]
            confidence = decision["confidence"]

            # Forced workflow for better reliability
            if not history:
                action = "plan_skill"
            elif len(history) == 1 and history[0]["action"] == "plan_skill":
                if skill_code:
                    action = "write_skill"
                else:
                    action = "plan_skill"
            elif len(history) >= 2:
                last = history[-1]
                if last["action"] == "write_skill" and last.get("result", {}).get(
                    "success"
                ):
                    action = "test_skill"
                elif last["action"] == "plan_skill" and skill_code:
                    action = "write_skill"

            print(f"  Action: {action} (confidence: {confidence:.0%})")

            if action == "complete":
                print("✅ Task complete!")
                return {"success": True, "result": skill_code, "iterations": iteration}

            elif action == "failed":
                print("❌ Task failed")
                return {
                    "success": False,
                    "error": "Max iterations or unrecoverable error",
                    "iterations": iteration,
                }

            result = self._execute_action(action, goal, coder_model, skill_code)
            history.append({"action": action, "result": result})

            if result.get("success"):
                print(f"  ✓ {result.get('message', 'Success')}")
                if "code" in result:
                    skill_code = result["code"]
                    print(f"    Generated {len(skill_code)} chars")
                if "output" in result:
                    print(f"    Output: {result['output'][:100]}")
            else:
                print(f"  ✗ {result.get('message', 'Failed')}")

            if result.get("success") and action == "test_skill":
                print("✅ Test passed, completing...")
                return {"success": True, "result": skill_code, "iterations": iteration}

        return {
            "success": False,
            "error": "Max iterations reached",
            "iterations": iteration,
        }

    def _vote_on_action(
        self, goal: str, iteration: int, history: list, skill_code: str
    ) -> Dict:
        """Use voting to decide next action."""
        history_text = (
            "\n".join(
                [
                    f"- {h['action']}: {h['result'].get('message', 'done')}"
                    for h in history[-3:]
                ]
            )
            if history
            else "Starting"
        )

        has_code = "yes" if skill_code else "no"
        tested = any(h["action"] == "test_skill" for h in history)

        if tested and any(
            h.get("result", {}).get("success")
            for h in history
            if h["action"] == "test_skill"
        ):
            return {"action": "complete", "confidence": 1.0, "votes": {}}

        prompt = f"""Decide next action for this task.

Task: {goal}
Iteration: {iteration}/12
History: {history_text}
Has code: {has_code}

Reply with ONE action:
- plan_skill (generate code)
- write_skill (save code)  
- test_skill (test code)
- complete (if working)

Action:"""

        return self.voter.vote(prompt)

    def _execute_action(
        self, action: str, goal: str, coder_model: str, skill_code: str
    ) -> Dict:
        """Execute an action using appropriate model."""

        if action == "plan_skill":
            return self._plan(goal, coder_model)

        elif action == "write_skill":
            return self._write(skill_code)

        elif action == "test_skill":
            return self._test(skill_code)

        else:
            return {"success": False, "message": f"Unknown action: {action}"}

    def _plan(self, goal: str, model: str) -> Dict:
        """Generate code for the goal."""
        prompt = f"""Write Python code for this task. Output ONLY the code.

Task: {goal}

CRITICAL RULES:
- NO input() calls - code must run without user interaction
- In __main__, use hardcoded test values and print results
- Example: if __name__ == "__main__": result = function(10); print(result)

Code:"""

        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 1000},
        )

        code = response["message"]["content"]

        if "```" in code:
            parts = code.split("```")
            if len(parts) > 1:
                code = parts[1]
                if code.startswith("python"):
                    code = code[6:]

        return {
            "success": True,
            "code": code.strip(),
            "message": f"Generated {len(code)} chars",
        }

    def _write(self, code: str) -> Dict:
        """Save code to file."""
        if not code:
            return {"success": False, "message": "No code to write"}

        workspace = Path("agent_workspace/skills")
        workspace.mkdir(parents=True, exist_ok=True)

        skill_file = workspace / "swarm_skill.py"
        skill_file.write_text(code)

        return {"success": True, "message": f"Saved to {skill_file}"}

    def _test(self, code: str) -> Dict:
        """Test the code."""
        if not code:
            return {"success": False, "message": "No code to test"}

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(
                ["python3", temp_path], capture_output=True, text=True, timeout=15
            )

            os.unlink(temp_path)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Test passed",
                    "output": result.stdout[:500],
                }
            else:
                return {
                    "success": False,
                    "message": f"Test failed: {result.stderr[:200]}",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Test timed out"}
        except Exception as e:
            return {"success": False, "message": f"Test error: {e}"}
