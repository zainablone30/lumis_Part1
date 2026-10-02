"""
Lightweight local translation layer so a single English-fine-tuned LUMIS LLM
can still converse fluently in Urdu/Arabic: translate user input -> English
for the LLM, translate LLM's English reply -> user's language for output.
"""
from transformers import MarianMTModel, MarianTokenizer
import functools

MODEL_REGISTRY = {
    ("ur", "en"): "Helsinki-NLP/opus-mt-ur-en",
    ("en", "ur"): "Helsinki-NLP/opus-mt-en-ur",
    ("ar", "en"): "Helsinki-NLP/opus-mt-ar-en",
    ("en", "ar"): "Helsinki-NLP/opus-mt-en-ar",
}


class TranslationService:
    def __init__(self):
        self._cache = {}

    @functools.lru_cache(maxsize=8)
    def _load(self, src, tgt):
        name = MODEL_REGISTRY.get((src, tgt))
        if not name:
            return None
        tok = MarianTokenizer.from_pretrained(name)
        model = MarianMTModel.from_pretrained(name)
        return tok, model

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        if src_lang == tgt_lang:
            return text
        loaded = self._load(src_lang, tgt_lang)
        if loaded is None:
            return text  # no model available, pass through
        tok, model = loaded
        batch = tok([text], return_tensors="pt", padding=True, truncation=True)
        gen = model.generate(**batch, max_length=256)
        return tok.decode(gen[0], skip_special_tokens=True)