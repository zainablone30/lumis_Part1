# home_monitoring/inactivity_monitor.py
import time


class InactivityMonitor:
    def __init__(self, inactivity_threshold_sec=2 * 3600, active_hours=(7, 22)):
        self.inactivity_threshold_sec = inactivity_threshold_sec
        self.active_hours = active_hours  # only alert during expected waking hours
        self.alerted = False

    def _within_active_hours(self):
        hour = time.localtime().tm_hour
        return self.active_hours[0] <= hour <= self.active_hours[1]

    def check(self, seconds_since_motion: float) -> bool:
        if not self._within_active_hours():
            return False
        if seconds_since_motion >= self.inactivity_threshold_sec and not self.alerted:
            self.alerted = True
            return True
        if seconds_since_motion < self.inactivity_threshold_sec:
            self.alerted = False
        return False