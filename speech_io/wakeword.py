import pvporcupine
import pyaudio
import struct

class WakeWordListener:
    def __init__(self, access_key, keyword="hey lumis", keyword_path=None):
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path] if keyword_path else None,
            keywords=None if keyword_path else ["porcupine"],
        )
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
            input=True, frames_per_buffer=self.porcupine.frame_length,
        )

    def listen_for_wakeword(self):
        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            if self.porcupine.process(pcm) >= 0:
                return True
