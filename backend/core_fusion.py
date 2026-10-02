"""Fuses facial + vocal emotion predictions into one confidence-weighted state."""

EMOTION_SET = ["Surprise", "Fear", "Disgust", "Happiness", "Sadness", "Anger", "Neutral"]

def fuse_emotions(face_result, voice_result, face_weight=0.6, voice_weight=0.4):
    """
    face_result / voice_result: (label, confidence) or None
    Returns: dict {emotion, confidence, source}
    """
    if face_result is None and voice_result is None:
        return {"emotion": "Neutral", "confidence": 0.0, "source": "default"}

    if face_result and not voice_result:
        return {"emotion": face_result[0], "confidence": face_result[1], "source": "face"}

    if voice_result and not face_result:
        return {"emotion": voice_result[0], "confidence": voice_result[1], "source": "voice"}

    face_label, face_conf = face_result
    voice_label, voice_conf = voice_result

    if face_label == voice_label:
        combined_conf = face_conf * face_weight + voice_conf * voice_weight
        return {"emotion": face_label, "confidence": combined_conf, "source": "fused"}

    # Disagreement → trust the higher-weighted, higher-confidence signal
    face_score = face_conf * face_weight
    voice_score = voice_conf * voice_weight
    if face_score >= voice_score:
        return {"emotion": face_label, "confidence": face_score, "source": "face_dominant"}
    return {"emotion": voice_label, "confidence": voice_score, "source": "voice_dominant"}