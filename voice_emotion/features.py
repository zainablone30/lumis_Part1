import librosa
import numpy as np


def extract_features(audio_path, sr=16000):
    y, _ = librosa.load(audio_path, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mel = librosa.feature.melspectrogram(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    rms = librosa.feature.rms(y=y)
    pitches, mags = librosa.piptrack(y=y, sr=sr)
    pitch_vals = pitches[mags > np.median(mags)]
    pitch_mean = np.mean(pitch_vals) if len(pitch_vals) else 0.0

    feat = np.concatenate([
        mfcc.mean(axis=1), chroma.mean(axis=1), mel.mean(axis=1),
        zcr.mean(axis=1), rms.mean(axis=1), [pitch_mean]
    ])
    return feat