import os
import tempfile
from typing import Optional, Dict, Any

class VoiceProcessor:
    """Voice processing module for speech-to-text and text-to-speech functionality."""

    def __init__(self):
        self.whisper_available = False
        self.gtts_available = False
        self.temp_dir = tempfile.gettempdir()

        # Try to import optional dependencies
        try:
            import whisper
            self.whisper_available = True
            self.whisper_model = None  # Lazy loading
            print("Whisper (speech-to-text) is available")
        except ImportError:
            print("Whisper not available. Install with: pip install openai-whisper")

        try:
            from gtts import gTTS
            self.gtts_available = True
            print("gTTS (text-to-speech) is available")
        except ImportError:
            print("gTTS not available. Install with: pip install gtts")

    def speech_to_text(self, audio_file_path: str, model: str = "base") -> str:
        """Convert speech audio file to text using Whisper."""
        if not self.whisper_available:
            return "Speech-to-text not available. Please install openai-whisper."

        if not os.path.exists(audio_file_path):
            return f"Audio file not found: {audio_file_path}"

        try:
            import whisper

            # Load model lazily
            if not self.whisper_model or self.whisper_model._model_name != model:
                print(f"Loading Whisper model: {model}")
                self.whisper_model = whisper.load_model(model)

            # Transcribe audio
            result = self.whisper_model.transcribe(audio_file_path)
            return result.get("text", "").strip()

        except Exception as e:
            return f"Speech-to-text error: {str(e)}"

    def text_to_speech(self, text: str, output_path: Optional[str] = None, language: str = "en") -> str:
        """Convert text to speech using Google Text-to-Speech."""
        if not self.gtts_available:
            return "Text-to-speech not available. Please install gtts."

        if not output_path:
            # Generate temporary filename
            import uuid
            filename = f"tts_output_{uuid.uuid4().hex[:8]}.mp3"
            output_path = os.path.join(self.temp_dir, filename)

        try:
            from gtts import gTTS

            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=False)

            # Save audio file
            tts.save(output_path)
            return output_path

        except Exception as e:
            raise Exception(f"Text-to-speech error: {str(e)}")

    def speech_to_speech(self, input_audio_path: str, output_audio_path: Optional[str] = None,
                        whisper_model: str = "base", tts_language: str = "en") -> str:
        """Convert speech to text and back to speech (speech-to-speech conversion)."""
        try:
            # Convert speech to text
            text = self.speech_to_text(input_audio_path, model=whisper_model)
            if "error" in text.lower() or not text.strip():
                return f"Speech-to-speech failed at speech-to-text stage: {text}"

            # Convert text back to speech
            output_file = self.text_to_speech(text, output_path, language=tts_language)
            return output_file

        except Exception as e:
            return f"Speech-to-speech error: {str(e)}"

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages for text-to-speech."""
        if not self.gtts_available:
            return {}

        # Common languages supported by gTTS
        languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi"
        }
        return languages

    def get_whisper_models(self) -> list:
        """Get available Whisper models."""
        if not self.whisper_available:
            return []

        return ["tiny", "base", "small", "medium", "large"]

    def is_available(self) -> Dict[str, bool]:
        """Check availability of voice processing features."""
        return {
            "speech_to_text": self.whisper_available,
            "text_to_speech": self.gtts_available,
            "speech_to_speech": self.whisper_available and self.gtts_available
        }

    def transcribe_file_with_metadata(self, audio_file_path: str, model: str = "base") -> Dict[str, Any]:
        """Transcribe audio file and return detailed metadata."""
        if not self.whisper_available:
            return {
                "text": "Speech-to-text not available",
                "error": "Whisper not installed"
            }

        try:
            import whisper

            # Load model
            if not self.whisper_model or self.whisper_model._model_name != model:
                print(f"Loading Whisper model: {model}")
                self.whisper_model = whisper.load_model(model)

            # Transcribe with detailed output
            result = self.whisper_model.transcribe(audio_file_path, verbose=True)

            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "model_used": model,
                "file_path": audio_file_path
            }

        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "file_path": audio_file_path
            }

    def create_audio_book_segment(self, text: str, chapter_num: int, output_dir: str = "audio_book") -> str:
        """Create an audio book segment with chapter naming."""
        if not self.gtts_available:
            raise Exception("Text-to-speech not available")

        os.makedirs(output_dir, exist_ok=True)
        filename = f"chapter_{chapter_num:03d}.mp3"
        output_path = os.path.join(output_dir, filename)

        return self.text_to_speech(text, output_path)