"""
Routes TTS synthesis to the correct backend per language:
 - XTTS-v2 (Coqui) for English / Arabic / most Latin-script languages
 - Facebook MMS-TTS for Urdu (and other low-resource languages XTTS lacks)
"""
import yaml
from TTS.api import TTS
from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile as wavfile

CONFIG = yaml.safe_load(open("supported_languages.yaml"))


class MultilingualTTS:
    def __init__(self):
        self.xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self._mms_cache = {}

    def _get_mms_model(self, model_name):
        if model_name not in self._mms_cache:
            tok = AutoTokenizer.from_pretrained(model_name)
            model = VitsModel.from_pretrained(model_name)
            self._mms_cache[model_name] = (tok, model)
        return self._mms_cache[model_name]

    def synthesize(self, text: str, lang_code: str, out_path="response.wav",
                    speaker_wav: str = None) -> str:
        lang_cfg = CONFIG["languages"].get(lang_code, CONFIG["languages"][CONFIG["languages"]["default"]])
        backend = lang_cfg.get("tts_backend", "xtts")

        if backend == "xtts":
            self.xtts.tts_to_file(
                text=text, file_path=out_path, language=lang_code,
                speaker_wav=speaker_wav or "default_speaker_ref.wav",
            )
        elif backend == "mms":
            tok, model = self._get_mms_model(lang_cfg["mms_model"])
            inputs = tok(text, return_tensors="pt")
            with torch.no_grad():
                output = model(**inputs).waveform
            wavfile.write(out_path, model.config.sampling_rate, output.squeeze().numpy())

        return out_path