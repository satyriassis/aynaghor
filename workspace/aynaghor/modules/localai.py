import os
import json
import requests
from typing import Optional, Dict, Any
from ..config import settings

class LocalAIClient:
    """Client for local AI models (Ollama, LM Studio, or custom APIs)."""

    def __init__(self):
        self.base_url = settings.get('LLM_HOST', 'http://localhost:8000')
        self.model = settings.get('LLM_MODEL', 'llama2')
        self.timeout = 60

        print(f"Local AI client initialized with host: {self.base_url}")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using local AI model."""
        try:
            # Try different API formats based on the service
            if self._is_ollama():
                return self._generate_ollama(prompt, **kwargs)
            elif self._is_lm_studio():
                return self._generate_lm_studio(prompt, **kwargs)
            else:
                return self._generate_generic(prompt, **kwargs)

        except Exception as e:
            return f"Local AI error: {str(e)}"

    def _is_ollama(self) -> bool:
        """Check if the endpoint is Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _is_lm_studio(self) -> bool:
        """Check if the endpoint is LM Studio."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _generate_ollama(self, prompt: str, **kwargs) -> str:
        """Generate using Ollama API."""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": self._format_prompt(prompt),
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "top_k": kwargs.get('top_k', 40),
                "top_p": kwargs.get('top_p', 0.95),
                "num_predict": kwargs.get('max_tokens', 2048),
            }
        }

        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        return data.get('response', 'No response generated.')

    def _generate_lm_studio(self, prompt: str, **kwargs) -> str:
        """Generate using LM Studio OpenAI-compatible API."""
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are AYNAGH0R, an AI assistant specialized in dark fantasy and erotic storytelling. You create engaging, imaginative content while maintaining appropriate boundaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 2048),
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            return "No response generated."

    def _generate_generic(self, prompt: str, **kwargs) -> str:
        """Generate using a generic OpenAI-compatible API."""
        url = f"{self.base_url}/v1/completions"

        payload = {
            "model": self.model,
            "prompt": self._format_prompt(prompt),
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 2048),
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['text']
            else:
                return "No response generated."

        except requests.exceptions.ConnectionError:
            return "Cannot connect to local AI service. Please ensure your local AI model is running."

    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for local AI."""
        system_prompt = """You are AYNAGH0R, an AI assistant specialized in dark fantasy and erotic storytelling.
You can create engaging, imaginative content in these genres while maintaining appropriate boundaries.
Be creative, descriptive, and respectful in your responses.

User:"""

        return f"{system_prompt}\n\n{prompt}"

    def is_available(self) -> bool:
        """Check if local AI service is available."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code < 500
        except:
            return False

    def get_available_models(self) -> list:
        """Get list of available models from the service."""
        try:
            if self._is_ollama():
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    return [model['name'] for model in models]

            elif self._is_lm_studio():
                response = requests.get(f"{self.base_url}/v1/models", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('data', [])
                    return [model['id'] for model in models]

        except:
            pass

        return []

    def test_connection(self) -> bool:
        """Test connection to local AI service."""
        try:
            test_response = self.generate("Hello", max_tokens=10)
            return len(test_response) > 0 and "error" not in test_response.lower()
        except:
            return False