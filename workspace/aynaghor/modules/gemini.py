import os
import json
import requests
from typing import Optional, Dict, Any
from ..config import settings

class GeminiClient:
    """Google Gemini API client for text generation."""

    def __init__(self):
        self.api_key = settings.get('GEMINI_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"  # Fast and capable model

        if not self.api_key:
            print("Warning: No Gemini API key provided. Gemini client will not be functional.")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Google Gemini API."""
        if not self.api_key:
            raise ValueError("Gemini API key not configured")

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        # Prepare the request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": self._format_prompt(prompt)
                }]
            }],
            "generationConfig": {
                "temperature": kwargs.get('temperature', 0.7),
                "topK": kwargs.get('top_k', 40),
                "topP": kwargs.get('top_p', 0.95),
                "maxOutputTokens": kwargs.get('max_tokens', 2048),
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return "I apologize, but I couldn't generate a response. Please try again."

        except requests.exceptions.RequestException as e:
            if response.status_code == 400:
                return "The request was invalid. Please check your input and try again."
            elif response.status_code == 403:
                return "Access denied. Please check your API key and permissions."
            elif response.status_code == 429:
                return "Rate limit exceeded. Please wait a moment and try again."
            else:
                return f"Network error occurred: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for Gemini API."""
        # Add system context for dark/erotic content generation
        system_prompt = """You are AYNAGH0R, an AI assistant specialized in dark fantasy and erotic storytelling.
        You can create engaging, imaginative content in these genres while maintaining appropriate boundaries.
        Be creative, descriptive, and respectful in your responses."""

        return f"{system_prompt}\n\nUser: {prompt}"

    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        return bool(self.api_key)

    def test_connection(self) -> bool:
        """Test connection to Gemini API."""
        try:
            test_response = self.generate("Hello", max_tokens=10)
            return len(test_response) > 0
        except:
            return False