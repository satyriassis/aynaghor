import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

class MemoryManager:
    """Simple JSON-based memory storage for conversation history and context."""

    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.max_messages = 1000  # Maximum messages to keep in memory
        self.conversation_history = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_messages": 0
        }

        # Load existing memory if file exists
        self.load_memory()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to conversation history."""
        message = {
            "role": role,  # user, assistant, system
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.conversation_history) + 1
        }

        if metadata:
            message["metadata"] = metadata

        self.conversation_history.append(message)
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.metadata["total_messages"] = len(self.conversation_history)

        # Keep only the last max_messages
        if len(self.conversation_history) > self.max_messages:
            self.conversation_history = self.conversation_history[-self.max_messages:]

        # Save to file
        self.save_memory()

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history, optionally limited to recent messages."""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()

    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent messages."""
        return self.conversation_history[-count:] if len(self.conversation_history) >= count else self.conversation_history

    def search_messages(self, query: str, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search messages by content and optionally by role."""
        results = []
        query_lower = query.lower()

        for message in self.conversation_history:
            if role and message.get("role") != role:
                continue

            if query_lower in message.get("content", "").lower():
                results.append(message)

        return results

    def clear_conversation(self) -> None:
        """Clear all conversation history."""
        self.conversation_history = []
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.metadata["total_messages"] = 0
        self.save_memory()

    def export_conversation(self, filename: Optional[str] = None) -> str:
        """Export conversation history to a file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_export_{timestamp}.json"

        export_data = {
            "metadata": self.metadata,
            "conversation": self.conversation_history,
            "exported_at": datetime.now().isoformat()
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return filename

    def import_conversation(self, filename: str) -> bool:
        """Import conversation history from a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "conversation" in data:
                self.conversation_history.extend(data["conversation"])
                self.metadata["last_updated"] = datetime.now().isoformat()
                self.metadata["total_messages"] = len(self.conversation_history)
                self.save_memory()
                return True

        except Exception as e:
            print(f"Error importing conversation: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the conversation history."""
        if not self.conversation_history:
            return {"total_messages": 0, "user_messages": 0, "assistant_messages": 0, "system_messages": 0}

        user_count = sum(1 for msg in self.conversation_history if msg.get("role") == "user")
        assistant_count = sum(1 for msg in self.conversation_history if msg.get("role") == "assistant")
        system_count = sum(1 for msg in self.conversation_history if msg.get("role") == "system")

        return {
            "total_messages": len(self.conversation_history),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "system_messages": system_count,
            "first_message_time": self.conversation_history[0].get("timestamp"),
            "last_message_time": self.conversation_history[-1].get("timestamp")
        }

    def save_memory(self) -> None:
        """Save memory to file."""
        try:
            data = {
                "metadata": self.metadata,
                "conversation_history": self.conversation_history
            }

            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving memory: {e}")

    def load_memory(self) -> None:
        """Load memory from file."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.conversation_history = data.get("conversation_history", [])
                self.metadata = data.get("metadata", self.metadata)

        except Exception as e:
            print(f"Error loading memory: {e}")
            self.conversation_history = []
            self.metadata = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_messages": 0
            }

    def add_memory_tag(self, message_id: int, tags: List[str]) -> None:
        """Add tags to a specific message."""
        for message in self.conversation_history:
            if message.get("id") == message_id:
                if "metadata" not in message:
                    message["metadata"] = {}
                message["metadata"]["tags"] = tags
                self.save_memory()
                break

    def get_messages_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all messages with a specific tag."""
        tagged_messages = []
        for message in self.conversation_history:
            tags = message.get("metadata", {}).get("tags", [])
            if tag in tags:
                tagged_messages.append(message)
        return tagged_messages