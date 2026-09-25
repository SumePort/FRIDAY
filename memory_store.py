import json
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Small JSON-backed persistent memory store."""

    def __init__(self, user_id: str, storage_path: str = "conversations"):
        safe_user_id = "".join(
            char if char.isalnum() or char in "-_" else "_"
            for char in user_id
        ).strip("_") or "default_user"

        self.user_id = safe_user_id
        self.storage_path = storage_path
        self.memory_file = os.path.join(
            storage_path, f"{self.user_id}_memory.json"
        )
        os.makedirs(storage_path, exist_ok=True)

    def load_memory(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.memory_file):
            return []

        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            logger.exception("Could not load memory file")
            return []

    @staticmethod
    def _as_dict(conversation: Any) -> dict[str, Any]:
        if hasattr(conversation, "model_dump"):
            return conversation.model_dump(mode="json")
        if hasattr(conversation, "dict"):
            return conversation.dict()
        if isinstance(conversation, dict):
            return conversation
        raise TypeError("conversation must be a dict-like object")

    @staticmethod
    def _conversation_key(conversation: dict[str, Any]) -> str:
        messages = conversation.get("messages", [])
        return json.dumps(
            messages,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

    def save_conversation(self, conversation: Any) -> bool:
        try:
            conversation_dict = self._as_dict(conversation)
            conversation_dict.setdefault(
                "timestamp",
                datetime.now().astimezone().isoformat(),
            )

            memory = self.load_memory()
            new_key = self._conversation_key(conversation_dict)

            if any(self._conversation_key(item) == new_key for item in memory):
                return True

            memory.append(conversation_dict)

            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump(
                    memory,
                    file,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

            return True
        except (OSError, TypeError, ValueError):
            logger.exception("Could not save conversation")
            return False

    def get_recent_context(self, max_messages: int = 30) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        for conversation in self.load_memory():
            items = conversation.get("messages", [])
            if isinstance(items, list):
                messages.extend(
                    item for item in items if isinstance(item, dict)
                )
        return messages[-max_messages:]

    def get_conversation_count(self) -> int:
        return len(self.load_memory())

    def clear_duplicates(self) -> int:
        memory = self.load_memory()
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()

        for conversation in memory:
            key = self._conversation_key(conversation)
            if key in seen:
                continue
            seen.add(key)
            unique.append(conversation)

        removed = len(memory) - len(unique)
        if removed:
            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump(
                    unique,
                    file,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

        return removed
