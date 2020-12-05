import numpy as np
import librosa
import matplotlib.pyplot as plt
import pandas as pd
import os
import math
import statistics
from multiprocessing import Pool, cpu_count
import numpy as np

class Tempo:
    def __init__(self):
        self.signal = []
        self.counter = 0
    def global_tempo(self, signal, sr):
        onset_env = librosa.onset.onset_strength(y=signal, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        print(tempo)
        return tempo