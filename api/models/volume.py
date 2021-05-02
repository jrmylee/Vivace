import statistics
import math
import numpy as np 
def get_average_power(x, fs, win_len_sec=0.1, power_ref=10**(-12)):
        win_len = round(win_len_sec * fs)
        win = np.ones(win_len) / win_len
        spec = 10 * np.log10(np.convolve(x**2, win, mode='same') / power_ref)
        spec = spec[spec > -1000]
        if len(spec) == 0:
            return 0
        mean_vol = statistics.mean(spec)
        volume = math.floor(mean_vol)
        return volume

def overlap_windowed_volume(signal, hop_size=1, win_len=3, sr=22050):
    tempos = []
    for i in range(0, len(signal) - win_len * sr, hop_size * sr):
        y_hat = signal[i : i + win_len * sr]
        tempo = get_average_power(y_hat, sr)
        tempos.append(tempo)

    return tempos[win_len // 2 :]
