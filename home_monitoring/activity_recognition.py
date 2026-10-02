# home_monitoring/activity_recognition.py
"""Rule-based activity classification from pose keypoints: standing/sitting/lying/walking."""
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose


class ActivityRecognizer:
    def __init__(self):
        self.pose = mp_pose.Pose(min_detection_confidence=0.5)
        self.prev_ankle_x = None

    def classify(self, frame_rgb) -> str:
        results = self.pose.process(frame_rgb)
        if not results.pose_landmarks:
            return "unknown"

        lm = results.pose_landmarks.landmark
        hip_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
        knee_y = (lm[mp_pose.PoseLandmark.LEFT_KNEE].y + lm[mp_pose.PoseLandmark.RIGHT_KNEE].y) / 2
        shoulder_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
        ankle_x = (lm[mp_pose.PoseLandmark.LEFT_ANKLE].x + lm[mp_pose.PoseLandmark.RIGHT_ANKLE].x) / 2

        torso_len = abs(hip_y - shoulder_y)
        leg_len = abs(knee_y - hip_y)

        moving = False
        if self.prev_ankle_x is not None:
            moving = abs(ankle_x - self.prev_ankle_x) > 0.02
        self.prev_ankle_x = ankle_x

        if torso_len < 0.12:  # body mostly horizontal in frame
            return "lying_down"
        if leg_len < torso_len * 0.3:
            return "sitting"
        if moving:
            return "walking"
        return "standing"