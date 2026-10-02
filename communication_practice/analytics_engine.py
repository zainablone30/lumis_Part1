# communication_practice/analytics_engine.py
import re

FILLER_WORDS = {"um", "uh", "like", "you know", "i mean", "sort of", "kind of", "basically", "actually"}


class CommunicationAnalytics:
    def analyze(self, asr_result: dict) -> dict:
        """
        asr_result: output of LumisASR.transcribe() -> {text, words:[{word,start,end}]}
        """
        words = asr_result["words"]
        text = asr_result["text"]

        if not words:
            return {"error": "No speech detected"}

        duration = words[-1]["end"] - words[0]["start"]
        word_count = len(words)
        wpm = (word_count / duration) * 60 if duration > 0 else 0

        # Pause detection
        pauses = []
        for i in range(1, len(words)):
            gap = words[i]["start"] - words[i - 1]["end"]
            if gap > 0.5:
                pauses.append(gap)
        pause_count = len(pauses)
        total_pause_time = sum(pauses)

        # Filler word rate
        tokens = re.findall(r"\b\w+\b", text.lower())
        filler_count = sum(1 for t in tokens if t in FILLER_WORDS)
        filler_rate = filler_count / word_count if word_count else 0

        # Vocabulary variety (type-token ratio)
        ttr = len(set(tokens)) / len(tokens) if tokens else 0

        clarity_score = self._compute_clarity(wpm, filler_rate, pause_count, word_count)

        return {
            "duration_sec": round(duration, 1),
            "word_count": word_count,
            "pace_wpm": round(wpm, 1),
            "pause_count": pause_count,
            "total_pause_time_sec": round(total_pause_time, 1),
            "filler_word_count": filler_count,
            "filler_rate": round(filler_rate, 3),
            "vocabulary_variety_ttr": round(ttr, 3),
            "clarity_score": clarity_score,
        }

    def _compute_clarity(self, wpm, filler_rate, pause_count, word_count):
        score = 100
        # Ideal conversational pace: 120-160 wpm
        if wpm < 100 or wpm > 180:
            score -= min(abs(wpm - 140) * 0.3, 25)
        score -= min(filler_rate * 200, 30)          # heavy filler usage penalty
        pause_ratio = pause_count / max(word_count, 1)
        score -= min(pause_ratio * 100, 20)
        return max(round(score, 1), 0)