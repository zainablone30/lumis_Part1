# home_monitoring/presence_detector.py
import mediapipe as mp
import time


class PresenceDetector:
    def __init__(self):
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        self.last_seen_ts = time.time()

    def update(self, frame_rgb) -> bool:
        results = self.detector.process(frame_rgb)
        present = bool(results.detections)
        if present:
            self.last_seen_ts = time.time()
        return present

    def seconds_since_last_seen(self) -> float:
        return time.time() - self.last_seen_ts