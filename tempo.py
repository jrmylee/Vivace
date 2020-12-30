import numpy as np
import librosa

class Tempo:
    def __init__(self):
        self.signal = []
        self.counter = 0
    def global_tempo(self, signal, sr):
        onset_env = librosa.onset.onset_strength(y=signal, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        return tempo[0]