# home_monitoring/monitoring_service.py
"""
Orchestrates the full home-monitoring pipeline. Runs as a background loop
consuming camera frames + audio chunks and dispatching alerts.
Consent-gated exactly like Grief Mode was in the original proposal.
"""
import cv2
import time
import threading
import numpy as np

from presence_detector import PresenceDetector
from fall_detection import FallDetector
from activity_recognition import ActivityRecognizer
from sound_anomaly import SoundAnomalyDetector
from inactivity_monitor import InactivityMonitor
from alert_manager import AlertManager


class HomeMonitoringService:
    def __init__(self, caregiver_contact="+92-300-0000000", consented=False):
        self.consented = consented   # must be explicitly set True via consent flow
        self.presence = PresenceDetector()
        self.fall_detector = FallDetector()
        self.activity_recognizer = ActivityRecognizer()
        self.sound_detector = SoundAnomalyDetector()
        self.inactivity_monitor = InactivityMonitor()
        self.alert_manager = AlertManager(caregiver_contact=caregiver_contact)

        self.running = False
        self.current_status = {
            "present": False, "activity": "unknown",
            "last_alert": None, "monitoring_active": False
        }

    def set_consent(self, consented: bool):
        self.consented = consented
        self.current_status["monitoring_active"] = consented

    def process_video_frame(self, frame_bgr):
        if not self.consented:
            return self.current_status

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        present = self.presence.update(frame_rgb)
        self.current_status["present"] = present

        if present:
            fall_result = self.fall_detector.process_frame(frame_rgb)
            if fall_result["fall_detected"]:
                msg = self.alert_manager.trigger(
                    "fall_detected",
                    {"torso_angle": fall_result["torso_angle"]},
                    severity="high",
                )
                self.current_status["last_alert"] = msg

            activity = self.activity_recognizer.classify(frame_rgb)
            self.current_status["activity"] = activity

        seconds_inactive = self.presence.seconds_since_last_seen()
        if self.inactivity_monitor.check(seconds_inactive):
            msg = self.alert_manager.trigger(
                "prolonged_inactivity",
                {"minutes_inactive": round(seconds_inactive / 60, 1)},
                severity="medium",
            )
            self.current_status["last_alert"] = msg

        return self.current_status

    def process_audio_chunk(self, audio_chunk: np.ndarray, sr=16000):
        if not self.consented:
            return

        result = self.sound_detector.analyze_chunk(audio_chunk, sr)
        if result["possible_distress_sound"]:
            msg = self.alert_manager.trigger(
                "distress_sound_detected",
                {"db_level": result["db_level"], "pitch_hz": result["avg_pitch_hz"]},
                severity="high",
            )
            self.current_status["last_alert"] = msg

    def get_status(self):
        return self.current_status

    def get_alert_history(self):
        return self.alert_manager.get_alert_history()