class VoiceProcessor:
    def __init__(self):
        self.whisper_available = False
        self.gtts_available = False

    def is_available(self):
        return {
            "speech_to_text": self.whisper_available,
            "text_to_speech": self.gtts_available,
            "speech_to_speech": self.whisper_available and self.gtts_available
        }