import whisper


class MultilingualASR:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str) -> dict:
        """Auto-detects language; returns text, language code, and word timings."""
        result = self.model.transcribe(audio_path, word_timestamps=True)
        words = []
        for seg in result["segments"]:
            for w in seg.get("words", []):
                words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})

        return {
            "text": result["text"].strip(),
            "language": result.get("language", "en"),
            "words": words,
        }