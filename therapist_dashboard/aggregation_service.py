"""Produces anonymized, aggregate-only analytics — no raw conversation text ever surfaces here."""
import sqlite3
import json
from collections import Counter
from datetime import datetime, timedelta


class AggregationService:
    def __init__(self, db_path="lumis.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def emotion_trend(self, user_id, days=30):
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            "SELECT emotion, created_at FROM emotion_logs WHERE user_id=? AND created_at>=?",
            (user_id, since)
        ).fetchall()
        counts = Counter(r[0] for r in rows)
        total = sum(counts.values()) or 1
        return {emo: round(c / total * 100, 1) for emo, c in counts.items()}

    def communication_progress(self, user_id):
        rows = self.conn.execute(
            "SELECT scenario, metrics_json, created_at FROM comm_scorecards WHERE user_id=? "
            "ORDER BY created_at ASC", (user_id,)
        ).fetchall()
        by_scenario = {}
        for scenario, metrics_json, ts in rows:
            metrics = json.loads(metrics_json)
            by_scenario.setdefault(scenario, []).append({
                "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                "clarity_score": metrics.get("clarity_score"),
                "filler_rate": metrics.get("filler_rate"),
                "pace_wpm": metrics.get("pace_wpm"),
            })
        return by_scenario

    def physiological_trend(self, user_id, days=30):
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            "SELECT stress_level, stress_score, created_at FROM physiological_logs "
            "WHERE user_id=? AND created_at>=? ORDER BY created_at ASC", (user_id, since)
        ).fetchall()
        return [{"date": r[2], "stress_score": r[1], "stress_level": r[0]} for r in rows]

    def alert_summary(self, user_id):
        # Only counts + types — never message content — surfaced to professionals
        rows = self.conn.execute(
            "SELECT alert_type, severity FROM monitoring_alerts"
        ).fetchall()
        counts = Counter(f"{t}:{s}" for t, s in rows)
        return dict(counts)