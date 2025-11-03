
import os
import json
from typing import Dict, Any, Optional
from .config import settings
from ..modules.gemini import GeminiClient
from ..modules.localai import LocalAIClient
from ..modules.memory import MemoryManager
from ..modules.voice import VoiceProcessor
from ..modules.image import ImageProcessor

class Engine:
    def __init__(self):
        self.use_gemini = settings.get('USE_GEMINI', False)

        # Initialize AI clients
        self.gemini_client = GeminiClient() if self.use_gemini else None
        self.localai_client = LocalAIClient() if not self.use_gemini else None

        # Initialize processing modules
        self.memory = MemoryManager()
        self.voice = VoiceProcessor()
        self.image = ImageProcessor()

        # Conversation context
        self.conversation_history = []

    def route(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Route prompt to appropriate AI client with context awareness."""
        try:
            # Add context if provided
            if context:
                prompt = self._format_prompt_with_context(prompt, context)

            # Store user message in memory
            self.memory.add_message("user", prompt)

            # Route to appropriate AI client
            if self.use_gemini and self.gemini_client:
                response = self.gemini_client.generate(prompt)
            elif self.localai_client:
                response = self.localai_client.generate(prompt)
            else:
                # Fallback response if no AI client is available
                response = self._generate_fallback_response(prompt)

            # Store AI response in memory
            self.memory.add_message("assistant", response)

            return response

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.memory.add_message("system", error_msg)
            return error_msg

    def _format_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Format prompt with additional context."""
        formatted_prompt = prompt

        if context.get("conversation_history"):
            history = context["conversation_history"]
            if len(history) > 0:
                formatted_prompt = f"Previous conversation:\n"
                for msg in history[-5:]:  # Last 5 messages
                    formatted_prompt += f"{msg['role']}: {msg['content']}\n"
                formatted_prompt += f"\nCurrent request: {prompt}"

        if context.get("mode"):
            mode = context["mode"]
            if mode == "creative":
                formatted_prompt = f"Creative writing mode: {formatted_prompt}"
            elif mode == "analytical":
                formatted_prompt = f"Analytical mode: {formatted_prompt}"
            elif mode == "dark_erotic":
                formatted_prompt = f"Dark & erotic storytelling mode: {formatted_prompt}"

        return formatted_prompt

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when AI clients are unavailable."""
        return f"""
I understand you're asking: "{prompt}"

Currently, I'm running in offline mode without an active AI connection.
To enable full functionality, please configure either:

1. Google Gemini API (set USE_GEMINI=true and GEMINI_KEY in environment)
2. Local AI model (configure LLM_HOST in environment)

For now, I can help with basic text processing and file operations through my built-in modules.
"""

    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.memory.get_conversation_history()

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.memory.clear_conversation()

    def process_voice_input(self, audio_file_path: str) -> str:
        """Process voice input and convert to text."""
        try:
            return self.voice.speech_to_text(audio_file_path)
        except Exception as e:
            return f"Voice processing error: {str(e)}"

    def generate_speech(self, text: str, output_path: str) -> bool:
        """Generate speech from text."""
        try:
            return self.voice.text_to_speech(text, output_path)
        except Exception as e:
            print(f"Speech generation error: {str(e)}")
            return False

    def process_image(self, image_path: str, prompt: str) -> str:
        """Process image with AI."""
        try:
            return self.image.analyze_image(image_path, prompt)
        except Exception as e:
            return f"Image processing error: {str(e)}"

    def generate_image(self, prompt: str, output_path: str) -> bool:
        """Generate image from text prompt."""
        try:
            return self.image.generate_image(prompt, output_path)
        except Exception as e:
            print(f"Image generation error: {str(e)}")
            return False
