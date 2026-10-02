"""
Remote photoplethysmography (rPPG): estimates heart rate from subtle color
changes in facial skin captured by the onboard camera — fully non-invasive,
no extra hardware needed.
"""
import numpy as np
import mediapipe as mp
from scipy.signal import butter, filtfilt, find_peaks
from collections import deque

mp_face_mesh = mp.solutions.face_mesh
FOREHEAD_LANDMARKS = [10, 338, 297, 332, 284, 251, 389, 356]  # forehead region


class RPPGHeartRateEstimator:
    def __init__(self, fps=30, window_seconds=10):
        self.fps = fps
        self.window_size = fps * window_seconds
        self.green_signal = deque(maxlen=self.window_size)
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=False, min_detection_confidence=0.6
        )

    def _extract_roi_mean(self, frame_rgb):
        h, w, _ = frame_rgb.shape
        results = self.face_mesh.process(frame_rgb)
        if not results.multi_face_landmarks:
            return None

        lm = results.multi_face_landmarks[0].landmark
        xs = [int(lm[i].x * w) for i in FOREHEAD_LANDMARKS]
        ys = [int(lm[i].y * h) for i in FOREHEAD_LANDMARKS]
        x1, x2 = max(min(xs), 0), min(max(xs), w)
        y1, y2 = max(min(ys), 0), min(max(ys), h)
        if x2 <= x1 or y2 <= y1:
            return None

        roi = frame_rgb[y1:y2, x1:x2]
        return roi[:, :, 1].mean()  # green channel — most sensitive to blood volume pulse

    def add_frame(self, frame_rgb):
        val = self._extract_roi_mean(frame_rgb)
        if val is not None:
            self.green_signal.append(val)

    def estimate_bpm(self):
        if len(self.green_signal) < self.window_size:
            return None  # need a full window first

        signal = np.array(self.green_signal)
        signal = signal - np.mean(signal)

        # Bandpass filter 0.7-4 Hz = 42-240 bpm
        nyq = 0.5 * self.fps
        low, high = 0.7 / nyq, 4.0 / nyq
        b, a = butter(3, [low, high], btype="band")
        filtered = filtfilt(b, a, signal)

        fft_vals = np.abs(np.fft.rfft(filtered))
        freqs = np.fft.rfftfreq(len(filtered), d=1.0 / self.fps)
        valid = (freqs >= 0.7) & (freqs <= 4.0)

        if not np.any(valid):
            return None

        peak_freq = freqs[valid][np.argmax(fft_vals[valid])]
        bpm = peak_freq * 60
        return round(float(bpm), 1)

    def estimate_hrv_proxy(self):
        """Rough heart-rate-variability proxy via peak-to-peak interval std-dev."""
        if len(self.green_signal) < self.window_size:
            return None
        signal = np.array(self.green_signal) - np.mean(self.green_signal)
        peaks, _ = find_peaks(signal, distance=self.fps * 0.4)
        if len(peaks) < 3:
            return None
        intervals = np.diff(peaks) / self.fps
        return round(float(np.std(intervals) * 1000), 1)  # ms