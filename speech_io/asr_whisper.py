import whisper

class LumisASR:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path):
        """Returns text + word-level timestamps (used by Communication Practice analytics)."""
        result = self.model.transcribe(audio_path, word_timestamps=True)
        words = []
        for seg in result["segments"]:
            for w in seg.get("words", []):
                words.append({"word": w["word"].strip(), "start": w["start"], "end": w["end"]})
        return {"text": result["text"], "words": words}
