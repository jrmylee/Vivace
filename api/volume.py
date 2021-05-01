import numpy as np
import statistics
import math

class Volume:
    def __init__(self, win_len_sec=0.1, power_ref=10**(-12)):
        self.win_len_sec = win_len_sec
        self.power_ref = power_ref
        
    def compute_power_dB(self, x, fs):
        """Computation of the signal power in dB
        
        Notebook: C1/C1S3_Dynamics.ipynb
        
        Args: 
            x: Signal (waveform) to be analyzed
            Fs: Sampling rate
            win_len_sec: Length (seconds) of the window
            power_ref: Reference power level (0 dB)
        
        Returns: 
            power_db: Signal power in dB
        """     
        win_len = round(self.win_len_sec * fs)
        win = np.ones(win_len) / win_len
        power_db = 10 * np.log10(np.convolve(x**2, win, mode='same') / self.power_ref)    
        return power_db
    
    def get_average_power(self, x, fs):
        win_len = round(self.win_len_sec * fs)
        win = np.ones(win_len) / win_len
        spec = 10 * np.log10(np.convolve(x**2, win, mode='same') / self.power_ref)
        spec = spec[spec > -1000]
        if len(spec) == 0:
            return 0
        mean_vol = statistics.mean(spec)
        volume = math.floor(mean_vol)
        return volume

    def overlap_windowed_volume(self, signal, hop_size=1, win_len=3, sr=22050):
        tempos = []
        for i in range(0, len(signal) - win_len * sr, hop_size * sr):
            y_hat = signal[i : i + win_len * sr]
            tempo = self.get_average_power(y_hat, sr)
            tempos.append(tempo)

        return tempos[win_len // 2 :]
    
