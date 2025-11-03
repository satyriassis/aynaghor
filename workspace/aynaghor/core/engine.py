import os
from typing import Dict, Any, Optional
from .config import settings

class Engine:
    def __init__(self):
        self.use_gemini = settings.get('USE_GEMINI', False)
        self.conversation_history = []

        # Initialize memory (simple version)
        self.memory = self

    def route(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Route prompt to appropriate AI client with context awareness."""
        try:
            # Add context if provided
            if context:
                prompt = self._format_prompt_with_context(prompt, context)

            # Store user message in memory
            self.add_message("user", prompt)

            # Route to appropriate AI client
            if self.use_gemini:
                response = self._generate_with_gemini(prompt)
            else:
                response = self._generate_fallback_response(prompt)

            # Store AI response in memory
            self.add_message("assistant", response)

            return response

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.add_message("system", error_msg)
            return error_msg

    def _format_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Format prompt with additional context."""
        formatted_prompt = prompt

        if context.get("mode"):
            mode = context["mode"]
            if mode == "creative":
                formatted_prompt = f"Creative writing mode: {formatted_prompt}"
            elif mode == "analytical":
                formatted_prompt = f"Analytical mode: {formatted_prompt}"
            elif mode == "dark_erotic":
                formatted_prompt = f"Dark & erotic storytelling mode: {formatted_prompt}"

        return formatted_prompt

    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate using Google Gemini API."""
        try:
            import requests

            if not settings.get('GEMINI_KEY'):
                return self._generate_fallback_response(prompt)

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings['GEMINI_KEY']}"

            payload = {
                "contents": [{
                    "parts": [{"text": self._format_prompt(prompt)}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000,
                }
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return self._generate_fallback_response(prompt)

        except Exception as e:
            return self._generate_fallback_response(prompt)

    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for AI."""
        system_prompt = """You are AYNAGH0R, an AI assistant specialized in dark fantasy and erotic storytelling.
        You can create engaging, imaginative content in these genres while maintaining appropriate boundaries.
        Be creative, descriptive, and respectful in your responses."""

        return f"{system_prompt}\n\nUser: {prompt}"

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when AI clients are unavailable."""
        return f"""I understand you're asking: "{prompt}"

Currently, I'm running in offline mode without an active AI connection.
To enable full functionality, please configure either:

1. Google Gemini API (set USE_GEMINI=true and GEMINI_KEY in environment)
2. Local AI model (configure LLM_HOST in environment)

For now, here's a simple response to your request:

*As a dark fantasy storyteller, I can help you create atmospheric tales filled with mystery, romance, and adventure. Whether you seek stories of forbidden love, ancient prophecies, or magical encounters, I'm here to craft narratives that explore the depths of human desire and imagination.*

What specific type of story would you like me to help you create?"""

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": str(len(self.conversation_history))
        })

    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.conversation_history.copy()

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []