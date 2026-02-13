"""
Intent classification - distinguish tasks from chat.
"""

from typing import Literal

ACTION_VERBS = [
    "create",
    "make",
    "build",
    "write",
    "generate",
    "implement",
    "fix",
    "debug",
    "refactor",
    "optimize",
    "delete",
    "remove",
    "add",
    "update",
    "modify",
    "change",
    "convert",
    "transform",
    "develop",
    "code",
    "program",
    "script",
    "design",
    "construct",
    "edit",
    "patch",
    "solve",
    "automate",
    "deploy",
    "set up",
]

QUESTION_STARTERS = [
    "what",
    "how",
    "why",
    "when",
    "where",
    "who",
    "which",
    "can you",
    "could you",
    "would you",
    "explain",
    "tell me",
    "describe",
    "help me understand",
    "what's",
    "what is",
    "is there",
    "are there",
    "do you",
    "does",
]


def classify_intent(input_text: str) -> Literal["task", "chat"]:
    """
    Classify input as 'task' or 'chat'.

    Rules:
    - If contains action verbs → task
    - If starts with question words → chat
    - Default → chat

    Args:
        input_text: User input string

    Returns:
        "task" or "chat"
    """
    input_lower = input_text.lower().strip()

    # Check for action verbs (task indicators)
    for verb in ACTION_VERBS:
        if f"{verb} " in input_lower:
            return "task"
        if input_lower.startswith(verb):
            return "task"

    # Check for question patterns (chat indicators)
    for starter in QUESTION_STARTERS:
        if input_lower.startswith(starter):
            return "chat"

    # Check for greetings and simple phrases
    greetings = [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "thanks",
        "thank you",
    ]
    for greeting in greetings:
        if input_lower == greeting or input_lower.startswith(f"{greeting} "):
            return "chat"

    # Check if it's a code request pattern
    code_patterns = [
        "function that",
        "script that",
        "program that",
        "code that",
        "class that",
        "module that",
        "api that",
    ]
    for pattern in code_patterns:
        if pattern in input_lower:
            return "task"

    # Default to chat
    return "chat"


def classify_intent_with_model(
    input_text: str, model: str = "qwen2.5:0.5b"
) -> Literal["task", "chat"]:
    """
    Use LLM for more accurate intent classification.

    Falls back to rule-based if LLM fails.
    """
    try:
        import ollama

        prompt = f"""Classify this input. Reply with ONLY "task" or "chat".

Input: "{input_text}"

Rules:
- task: wants code created, modified, debugged, or file operations
- chat: asking questions, explanations, or general conversation

Classification:"""

        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 5, "temperature": 0.1},
        )

        result = response["message"]["content"].lower().strip()

        if "task" in result:
            return "task"
        elif "chat" in result:
            return "chat"
    except Exception:
        pass

    # Fallback to rule-based
    return classify_intent(input_text)
