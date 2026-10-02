"""
Background orchestrator: runs rPPG on camera frames + polls GSR sensor,
exposes a live stress reading consumed by the Companion Core (to proactively
offer grounding exercises) and the Home Monitoring module (to escalate
alerts if a fall/distress sound coincides with high physiological stress).
"""
import threading
import time

from rppg_heart_rate import RPPGHeartRateEstimator
from gsr_sensor import GSRSensor
from stress_classifier import StressClassifier


class PhysiologicalSensingService:
    def __init__(self):
        self.hr_estimator = RPPGHeartRateEstimator()
        self.gsr_sensor = GSRSensor()
        self.classifier = StressClassifier()
        self.latest_reading = {"stress_level": "Low", "stress_score": 0}
        self._lock = threading.Lock()
        self._running = False

    def process_camera_frame(self, frame_rgb, facial_emotion="Neutral"):
        self.hr_estimator.add_frame(frame_rgb)
        hr = self.hr_estimator.estimate_bpm()
        hrv = self.hr_estimator.estimate_hrv_proxy()
        self.classifier.update_baseline(hr)

        gsr_result = self.gsr_sensor.read_conductance_level()
        scr_peaks = self.gsr_sensor.detect_scr_peaks()

        result = self.classifier.classify(hr, hrv, gsr_result, scr_peaks, facial_emotion)
        result.update({"heart_rate_bpm": hr, "hrv_ms": hrv, "gsr": gsr_result})

        with self._lock:
            self.latest_reading = result
        return result

    def get_latest(self):
        with self._lock:
            return dict(self.latest_reading)

    def start_background_gsr_polling(self, interval_sec=2):
        """Keeps GSR readings flowing even between camera frame updates."""
        self._running = True

        def loop():
            while self._running:
                self.gsr_sensor.read_conductance_level()
                time.sleep(interval_sec)

        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self._running = False