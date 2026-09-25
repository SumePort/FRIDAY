import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from memory_store import ConversationMemory

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """Persist newly added LiveKit conversation items."""

    def __init__(self, user_id: str | None = None, poll_interval: float = 1.0):
        self.user_id = user_id or os.getenv("FRIDAY_USER_ID", "default_user")
        self.poll_interval = poll_interval
        self.saved_message_count = 0

    @staticmethod
    def _serialize(message: Any) -> dict:
        if hasattr(message, "model_dump"):
            return message.model_dump(mode="json")
        if hasattr(message, "dict"):
            return message.dict()
        if isinstance(message, dict):
            return message
        return {"content": str(message)}

    async def run(self, history: Any) -> None:
        memory = ConversationMemory(self.user_id)

        while True:
            await asyncio.sleep(self.poll_interval)

            try:
                messages = list(history.items)
            except Exception:
                logger.exception("Could not read LiveKit conversation history")
                continue

            if len(messages) <= self.saved_message_count:
                continue

            new_messages = messages[self.saved_message_count:]

            for message in new_messages:
                serialized = self._serialize(message)
                conversation = {
                    "messages": [serialized],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                if memory.save_conversation(conversation):
                    logger.info("Saved conversation item")
                else:
                    logger.error("Failed to save conversation item")

            self.saved_message_count = len(messages)
