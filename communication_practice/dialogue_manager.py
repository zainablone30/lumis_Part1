# communication_practice/dialogue_manager.py
import requests
from scenarios import SCENARIOS

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "lumis"


class ScenarioSession:
    def __init__(self, scenario_key: str, user_id: str):
        if scenario_key not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_key}")
        self.scenario = SCENARIOS[scenario_key]
        self.user_id = user_id
        self.history = [{"role": "assistant", "text": self.scenario["opening_line"]}]

    def respond(self, user_text: str) -> str:
        self.history.append({"role": "user", "text": user_text})

        convo = "\n".join(f"{h['role'].capitalize()}: {h['text']}" for h in self.history)
        prompt = (
            f"{self.scenario['system_prompt']}\n\n"
            f"Conversation so far:\n{convo}\n\nYour next line:"
        )

        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False,
                   "options": {"temperature": 0.75}}
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        reply = resp.json().get("response", "").strip()

        self.history.append({"role": "assistant", "text": reply})
        return reply

    def get_transcript(self):
        return self.history