# home_monitoring/alert_manager.py
"""
Central alert dispatcher. Generates a natural-language caregiver message via the
LUMIS LLM, logs it, and sends it through configured channel(s).
Replace the stub send functions with real Twilio/SMTP/Pushbullet credentials.
"""
import sqlite3
import time
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "lumis"


class AlertManager:
    def __init__(self, db_path="lumis.db", caregiver_contact=None):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.caregiver_contact = caregiver_contact
        self._init_table()

    def _init_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT, message TEXT, severity TEXT, created_at REAL, acknowledged INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def _generate_message(self, alert_type, details) -> str:
        prompt = (
            "You are LUMIS, a home-monitoring companion. Write a short, calm, "
            "non-alarming message (2-3 sentences) to a caregiver about the "
            f"following event: type={alert_type}, details={details}. "
            "Be clear and actionable but avoid causing panic."
        )
        try:
            resp = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME, "prompt": prompt, "stream": False
            }, timeout=15)
            return resp.json().get("response", "").strip()
        except Exception:
            return f"LUMIS Alert ({alert_type}): {details}"

    def trigger(self, alert_type: str, details: dict, severity="medium"):
        message = self._generate_message(alert_type, details)
        self.conn.execute(
            "INSERT INTO monitoring_alerts (alert_type, message, severity, created_at) VALUES (?,?,?,?)",
            (alert_type, message, severity, time.time())
        )
        self.conn.commit()
        self._dispatch(message, severity)
        return message

    def _dispatch(self, message, severity):
        # TODO: integrate real SMS/push notification service, e.g.:
        # twilio_client.messages.create(body=message, to=self.caregiver_contact, from_=TWILIO_NUMBER)
        print(f"[ALERT - {severity.upper()}] -> {self.caregiver_contact}: {message}")

    def get_alert_history(self, limit=50):
        rows = self.conn.execute(
            "SELECT alert_type, message, severity, created_at, acknowledged "
            "FROM monitoring_alerts ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [{"type": r[0], "message": r[1], "severity": r[2],
                  "created_at": r[3], "acknowledged": bool(r[4])} for r in rows]