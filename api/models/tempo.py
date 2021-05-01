import numpy as np
import librosa
from sklearn.metrics import mean_squared_error
from scipy.signal import medfilt

def windowed_tempo(signal, win_len=3, sr=22050):
    win, lx = win_len * sr, len(signal)
    new_len = int(np.ceil(lx/win)) * win

    signal = np.pad(signal, (0, new_len - lx), 'constant')
    signal = signal.reshape(new_len // win, win)

    tempos = []
    for x in signal:
        tempo = global_tempo(x, sr)
        tempos.append(tempo)
    return tempos

def median_windowed_tempo(signal, win_len=1, sr=22050, output_win_len=3):
    win, lx = win_len * sr, len(signal)
    new_len = int(np.ceil(lx/win)) * win

    signal = np.pad(signal, (0, new_len - lx), 'constant')
    signal = signal.reshape(new_len // win, win)

    tempos = []
    win_tempos, count = [], 0
    for x in signal:
        tempo = global_tempo(x, sr)
        win_tempos.append(tempo)
        if count == output_win_len:
            tempos.append(medfilt(win_tempos)[1])
            win_tempos, count = [], 0
        count += 1
    return tempos


def overlap_windowed_tempo(signal, hop_size=1, win_len=3, sr=22050):
    tempos = []
    for i in range(0, len(signal) - win_len * sr, hop_size * sr):
        y_hat = signal[i : i + win_len * sr]
        tempo = global_tempo(y_hat, sr)
        tempos.append(tempo)

    return tempos[win_len // 2 :]
    
def global_tempo(signal, sr):
    onset_env = librosa.onset.onset_strength(y=signal, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    return tempo[0]
# groundtruth data is in format of [tempo, time(ms), tempo, time, end, time, etc...]
# tempos is in the form [t1, t2, t3,...,tn], where ti is the tempo in window i
# generates signals for tempo vs time(seconds) and returns mean_squared_error, signal1, signal2
def evaluate(gt, tempos, sr=22050, win_len=3):
    gt_tempos = []
    for pair in gt:
        gt_tempos += [pair[0]] * (pair[1] // 1000)
    gt_signal = np.array(gt_tempos)

    c_tempos = []
    n = len(tempos)
    for i in range(n):
        c_tempos += [tempos[i] for j in range(win_len)]
    
    signal = np.array(c_tempos)
    length = min(len(signal), len(gt))
    error = mean_squared_error(gt_signal[0: length], signal[0: length])
    
    return error, signal, gt_signal

def evaluate2(gt, tempos, sr=22050, win_len=3):
    gt_tempos = []
    for pair in gt:
        gt_tempos += [pair[0]] * (pair[1] // 1000)
    gt_signal = np.array(gt_tempos)

    c_tempos = []
    n = len(tempos)
    for i in range(n):
        c_tempos.append(tempos[i])
    
    signal = np.array(c_tempos)
    length = min(len(signal), len(gt))
    error = mean_squared_error(gt_signal[0: length], signal[0: length])
    
    return error, signal, gt_signal