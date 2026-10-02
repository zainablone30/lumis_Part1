"""Maps detected emotion -> facial blend-shape targets for the 3D avatar."""

EMOTION_BLENDSHAPES = {
    "Happiness": {"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8, "eyeSquintLeft": 0.3,
                  "eyeSquintRight": 0.3, "browInnerUp": 0.1},
    "Sadness":   {"mouthFrownLeft": 0.6, "mouthFrownRight": 0.6, "browInnerUp": 0.7,
                  "browDownLeft": 0.2, "browDownRight": 0.2, "eyeBlinkLeft": 0.2, "eyeBlinkRight": 0.2},
    "Anger":     {"browDownLeft": 0.8, "browDownRight": 0.8, "mouthFrownLeft": 0.4,
                  "mouthFrownRight": 0.4, "noseSneerLeft": 0.3, "noseSneerRight": 0.3},
    "Fear":      {"browInnerUp": 0.8, "eyeWideLeft": 0.6, "eyeWideRight": 0.6, "jawOpen": 0.15},
    "Surprise":  {"browInnerUp": 0.9, "browOuterUpLeft": 0.8, "browOuterUpRight": 0.8,
                  "eyeWideLeft": 0.7, "eyeWideRight": 0.7, "jawOpen": 0.3},
    "Disgust":   {"noseSneerLeft": 0.6, "noseSneerRight": 0.6, "mouthFrownLeft": 0.3,
                  "mouthFrownRight": 0.3},
    "Neutral":   {},
}


class ExpressionController:
    def get_blendshapes(self, emotion: str, intensity: float = 1.0) -> dict:
        base = EMOTION_BLENDSHAPES.get(emotion, {})
        return {k: round(v * intensity, 3) for k, v in base.items()}

    def blend_with_lipsync(self, emotion_shapes: dict, lipsync_frame: dict) -> dict:
        """Merge emotion-driven blendshapes with current-frame lip-sync jaw value."""
        combined = dict(emotion_shapes)
        combined["jawOpen"] = max(combined.get("jawOpen", 0), lipsync_frame.get("jawOpen", 0))
        combined["mouthFunnel"] = lipsync_frame.get("mouthFunnel", 0)
        return combined