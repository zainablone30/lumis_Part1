# home_monitoring/fall_detection.py
"""
Rule-based fall detection using MediaPipe Pose keypoints.
Heuristic: torso-angle-from-vertical crosses threshold AND vertical drop of hip
center happens within a short time window -> fall candidate. Confirmed fall if
the person remains horizontal for several consecutive frames.
"""
import mediapipe as mp
import numpy as np
import time
import math

mp_pose = mp.solutions.pose


class FallDetector:
    def __init__(self, angle_thresh=55, confirm_frames=8):
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.angle_thresh = angle_thresh          # degrees from vertical
        self.confirm_frames = confirm_frames
        self.horizontal_streak = 0
        self.prev_hip_y = None
        self.prev_time = None

    def _torso_angle(self, landmarks):
        ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

        shoulder_mid = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2])
        hip_mid = np.array([(lh.x + rh.x) / 2, (lh.y + rh.y) / 2])

        dx, dy = shoulder_mid[0] - hip_mid[0], shoulder_mid[1] - hip_mid[1]
        angle_from_vertical = math.degrees(math.atan2(abs(dx), abs(dy) + 1e-6))
        return angle_from_vertical, hip_mid[1]

    def process_frame(self, frame_rgb) -> dict:
        results = self.pose.process(frame_rgb)
        now = time.time()

        if not results.pose_landmarks:
            self.horizontal_streak = 0
            return {"fall_detected": False, "reason": "no_person"}

        landmarks = results.pose_landmarks.landmark
        angle, hip_y = self._torso_angle(landmarks)

        sudden_drop = False
        if self.prev_hip_y is not None and self.prev_time is not None:
            dt = now - self.prev_time
            if dt > 0:
                vertical_speed = (hip_y - self.prev_hip_y) / dt
                sudden_drop = vertical_speed > 0.8  # normalized coords/sec

        self.prev_hip_y, self.prev_time = hip_y, now

        is_horizontal = angle > self.angle_thresh
        if is_horizontal:
            self.horizontal_streak += 1
        else:
            self.horizontal_streak = 0

        fall_confirmed = self.horizontal_streak >= self.confirm_frames and sudden_drop

        return {
            "fall_detected": fall_confirmed,
            "torso_angle": round(angle, 1),
            "horizontal_streak": self.horizontal_streak,
            "sudden_drop": sudden_drop,
        }