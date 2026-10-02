"""
Two-stage detection: Whisper's own language detection (from audio) is the
primary signal; langdetect on the transcribed text is a fallback / sanity check.
"""
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

SUPPORTED = {"en", "ur", "ar"}


class LanguageDetector:
    def detect_from_text(self, text: str) -> str:
        try:
            code = detect(text)
            return code if code in SUPPORTED else "en"
        except Exception:
            return "en"

    def resolve(self, whisper_lang: str, text: str) -> str:
        if whisper_lang in SUPPORTED:
            return whisper_lang
        return self.detect_from_text(text)