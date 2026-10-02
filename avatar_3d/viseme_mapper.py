"""
Converts TTS audio into a frame-by-frame lip-sync animation stream.
Uses amplitude-envelope-based jaw movement (works with ANY TTS engine,
no phoneme alignment required) + optional phoneme-based viseme refinement
if eSpeak-NG phoneme timestamps are available.
"""
import numpy as np
import librosa

# ARPAbet phoneme -> simplified viseme mapping (Preston Blair set)
PHONEME_VISEME_MAP = {
    "AA": "AI", "AE": "AI", "AH": "AI", "AO": "O", "AW": "O", "AY": "AI",
    "B": "MBP", "P": "MBP", "M": "MBP",
    "CH": "etc", "JH": "etc", "SH": "etc", "ZH": "etc",
    "D": "etc", "T": "etc", "N": "etc", "L": "etc",
    "EH": "E", "ER": "E", "EY": "E",
    "F": "FV", "V": "FV",
    "IH": "E", "IY": "E",
    "OW": "O", "OY": "O", "UH": "U", "UW": "U",
    "S": "etc", "Z": "etc", "TH": "etc", "DH": "etc",
    "W": "WQ", "R": "etc",
    "sil": "rest",
}


class VisemeMapper:
    def __init__(self, fps=30):
        self.fps = fps

    def from_audio_envelope(self, audio_path: str) -> list:
        """
        Primary method — engine-agnostic. Returns per-frame jaw-open values
        in [0,1] synced to audio, usable directly as a morph-target weight.
        """
        y, sr = librosa.load(audio_path, sr=16000)
        hop_length = int(sr / self.fps)
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

        # Normalize + smooth
        rms = rms / (np.max(rms) + 1e-6)
        smoothed = np.convolve(rms, np.ones(3) / 3, mode="same")

        frames = []
        for i, val in enumerate(smoothed):
            frames.append({
                "frame": i,
                "time": round(i / self.fps, 3),
                "jawOpen": round(float(np.clip(val * 1.3, 0, 1)), 3),
                "mouthFunnel": round(float(np.clip(val * 0.4, 0, 1)), 3),
            })
        return frames

    def from_phonemes(self, phoneme_timeline: list) -> list:
        """
        Optional refinement if you generate phoneme timings via eSpeak-NG
        (espeak-ng --phonout). phoneme_timeline: [{phoneme, start, end}]
        """
        frames = []
        for p in phoneme_timeline:
            viseme = PHONEME_VISEME_MAP.get(p["phoneme"].upper(), "rest")
            frames.append({
                "start": p["start"], "end": p["end"], "viseme": viseme
            })
        return frames