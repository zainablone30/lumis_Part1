from TTS.api import TTS

class LumisTTS:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        self.tts = TTS(model_name)

    def speak_to_file(self, text, out_path="response.wav", emotion="Neutral"):
        speed_map = {"Sadness": 0.9, "Fear": 1.05, "Anger": 1.0, "Happiness": 1.1, "Neutral": 1.0}
        self.tts.tts_to_file(text=text, file_path=out_path,
                              speed=speed_map.get(emotion, 1.0))
        return out_path
