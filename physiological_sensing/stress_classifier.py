"""Fuses rPPG heart-rate/HRV, GSR, and facial emotion into one stress score."""


class StressClassifier:
    def __init__(self):
        self.resting_hr_baseline = None
        self.hr_samples_for_baseline = []

    def update_baseline(self, hr):
        if hr is None:
            return
        self.hr_samples_for_baseline.append(hr)
        if len(self.hr_samples_for_baseline) > 30:
            self.hr_samples_for_baseline.pop(0)
        self.resting_hr_baseline = sum(self.hr_samples_for_baseline) / len(self.hr_samples_for_baseline)

    def classify(self, hr, hrv_ms, gsr_result, scr_peak_count, facial_emotion) -> dict:
        score = 0
        reasons = []

        if hr is not None and self.resting_hr_baseline:
            hr_elevation = hr - self.resting_hr_baseline
            if hr_elevation > 15:
                score += 35
                reasons.append("elevated heart rate")
            elif hr_elevation > 8:
                score += 15
                reasons.append("mildly elevated heart rate")

        if hrv_ms is not None and hrv_ms < 30:
            score += 20
            reasons.append("reduced heart-rate variability")

        if gsr_result and gsr_result["deviation"] > 0.15:
            score += 20
            reasons.append("elevated skin conductance")

        if scr_peak_count and scr_peak_count >= 3:
            score += 15
            reasons.append("frequent skin-conductance spikes")

        if facial_emotion in ("Fear", "Anger", "Sadness"):
            score += 10
            reasons.append(f"facial expression ({facial_emotion})")

        score = min(score, 100)
        if score >= 60:
            level = "High"
        elif score >= 30:
            level = "Moderate"
        else:
            level = "Low"

        return {"stress_score": score, "stress_level": level, "contributing_factors": reasons}