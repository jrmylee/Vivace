import numpy as np
import librosa
from sklearn.metrics import mean_squared_error

class Tempo:
    def __init__(self):
        self.signal = []
        self.counter = 0
    def global_tempo(self, signal, sr):
        onset_env = librosa.onset.onset_strength(y=signal, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        return tempo[0]
    # groundtruth data is in format of [start, end, time(ms), end, time, end, time, etc...]
    # tempos is in the form [t1, t2, t3,...,tn], where ti is the tempo in window i
    def evaluate(self, gt, tempos, sr=44000, win_len=3):
        start, end, time = gt[0], gt[1], gt[2] // 1000
        gt_tempos = list(np.linspace(start,end, time + 1))
        
        if len(gt) > 3:
            for i in range(3, len(gt)-1, 2):
                start, end, time = end, gt[i], gt[i+1] // 1000
                gt_tempos += list(np.linspace(start, end, time + 1))[1:]
            
        gt_signal = np.array(gt_tempos)
        print(gt_signal)
        c_tempos = []
        n = len(tempos)
        for i in range(n):
            c_tempos += [tempos[i] for j in range(win_len - 1)]
        
        signal = np.array(c_tempos)
        print(signal)
        
        error = mean_squared_error(gt_signal, signal)
        
        return error, signal, gt_signal
    def overlap_windowed_tempo(self, signal, hop_size=1, win_len=3, sr=22050):
        tempos = []
        for i in range(0, len(signal) - win_len * sr, hop_size * sr):
            y_hat = signal[i : i + win_len * sr]
            tempo = self.global_tempo(y_hat, sr)
            tempos.append(tempo)

        return tempos[win_len // 2 :]
    
            