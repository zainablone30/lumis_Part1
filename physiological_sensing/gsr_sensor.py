"""
Galvanic Skin Response sensor interface (e.g. Grove GSR sensor -> ADS1115
ADC -> Raspberry Pi I2C). Falls back to a simulated signal if hardware
libraries aren't present, so the software stack is fully testable before
hardware is wired in.
"""
import time
import random

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False


class GSRSensor:
    def __init__(self, channel=0, baseline_samples=50):
        self.channel = channel
        self.baseline = None
        self.baseline_samples = baseline_samples
        self.history = []

        if HARDWARE_AVAILABLE:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(i2c)
            self.chan = AnalogIn(self.ads, getattr(ADS, f"P{channel}"))
        else:
            self.ads = None

    def read_raw(self) -> float:
        if HARDWARE_AVAILABLE:
            return self.chan.voltage
        # Simulation mode: slow baseline drift + occasional "arousal" spikes
        base = 1.5 + 0.05 * (random.random() - 0.5)
        spike = 0.3 if random.random() < 0.05 else 0.0
        return base + spike

    def calibrate_baseline(self):
        samples = [self.read_raw() for _ in range(self.baseline_samples)]
        self.baseline = sum(samples) / len(samples)
        return self.baseline

    def read_conductance_level(self) -> dict:
        if self.baseline is None:
            self.calibrate_baseline()

        raw = self.read_raw()
        self.history.append((time.time(), raw))
        self.history = self.history[-300:]  # keep last ~5 min at 1Hz

        deviation = raw - self.baseline
        return {
            "raw_voltage": round(raw, 4),
            "baseline": round(self.baseline, 4),
            "deviation": round(deviation, 4),
            "hardware_connected": HARDWARE_AVAILABLE,
        }

    def detect_scr_peaks(self, window_sec=60):
        """Skin Conductance Response peak count in the recent window — a
        standard proxy for arousal/stress events."""
        from scipy.signal import find_peaks
        now = time.time()
        recent = [v for t, v in self.history if now - t <= window_sec]
        if len(recent) < 5:
            return 0
        peaks, _ = find_peaks(recent, prominence=0.05)
        return len(peaks)