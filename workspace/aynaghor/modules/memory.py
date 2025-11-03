class MemoryManager:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role: str, content: str, metadata=None):
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": str(len(self.conversation_history))
        })

    def get_conversation_history(self):
        return self.conversation_history.copy()

    def get_statistics(self):
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": sum(1 for msg in self.conversation_history if msg.get("role") == "user"),
            "assistant_messages": sum(1 for msg in self.conversation_history if msg.get("role") == "assistant"),
        }

    def clear_conversation(self):
        self.conversation_history = []

    def export_conversation(self, filename):
        import json
        data = {
            "conversation": self.conversation_history,
            "exported_at": str(len(self.conversation_history))
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename