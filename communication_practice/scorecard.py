# communication_practice/scorecard.py
import sqlite3
import json
import time


class ScorecardStore:
    def __init__(self, db_path="lumis.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS comm_scorecards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT, scenario TEXT, metrics_json TEXT, created_at REAL
            )
        """)
        self.conn.commit()

    def save(self, user_id, scenario, metrics: dict):
        self.conn.execute(
            "INSERT INTO comm_scorecards (user_id, scenario, metrics_json, created_at) VALUES (?,?,?,?)",
            (user_id, scenario, json.dumps(metrics), time.time())
        )
        self.conn.commit()

    def history(self, user_id, scenario=None):
        q = "SELECT scenario, metrics_json, created_at FROM comm_scorecards WHERE user_id=?"
        params = [user_id]
        if scenario:
            q += " AND scenario=?"
            params.append(scenario)
        q += " ORDER BY created_at ASC"
        rows = self.conn.execute(q, params).fetchall()
        return [{"scenario": r[0], "metrics": json.loads(r[1]), "created_at": r[2]} for r in rows]

    def progress_trend(self, user_id, scenario):
        hist = self.history(user_id, scenario)
        if len(hist) < 2:
            return {"trend": "insufficient_data"}
        first, last = hist[0]["metrics"], hist[-1]["metrics"]
        return {
            "clarity_change": last["clarity_score"] - first["clarity_score"],
            "filler_rate_change": last["filler_rate"] - first["filler_rate"],
            "sessions_completed": len(hist),
        }