"""
Core conversational engine: combines persona, RAG memory, detected emotion,
and crisis detection, then calls the locally hosted Ollama model.
"""
import os
import requests
from memory_rag import LumisMemory
from crisis_detection import CrisisDetector

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "lumis"

PERSONA_PATH = os.path.join(os.path.dirname(__file__), "persona_system_prompt.txt")
PERSONA = open(PERSONA_PATH).read()


class LumisLLMEngine:
    def __init__(self, user_id="default_user", user_name="Friend"):
        self.memory = LumisMemory(user_id=user_id)
        self.crisis_detector = CrisisDetector()
        self.user_name = user_name

    def chat(self, user_message: str, detected_emotion: str = "Neutral") -> dict:
        is_crisis = self.crisis_detector.check(user_message)
        context_block = self.memory.build_context_block(user_message)

        prompt = (
            f"{PERSONA}\n\n"
            f"User's name: {self.user_name}\n"
            f"Detected emotion this turn: {detected_emotion}\n"
            f"{context_block}\n\n"
            f"User: {user_message}\n"
            f"LUMIS:"
        )

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9},
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
            resp.raise_for_status()
            reply = resp.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            reply = ("I'm having trouble reaching my language model right now "
                      f"(is Ollama running?). Error: {e}")

        if is_crisis:
            reply = f"{self.crisis_detector.get_response_prefix()}\n\n{reply}"

        self.memory.add_turn("user", user_message, detected_emotion)
        self.memory.add_turn("assistant", reply, detected_emotion)

        return {
            "reply": reply,
            "crisis_flag": is_crisis,
            "detected_emotion": detected_emotion,
        }
