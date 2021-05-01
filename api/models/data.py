#!/usr/bin/env python
# coding: utf-8

# In[350]:


import numpy as np
import IPython.display as ipd
from matplotlib import pyplot as plt
import librosa.display
import soundfile as sf
import csv
from scipy import signal 
from sklearn.metrics import mean_squared_error
import os

np.random.seed(246810)

sr = 22050
ten = np.zeros(sr * 10)
# returns y with an impulse at every m millisecond
def metro(y, m):
    sr = 22050 // 1000 # samples per milisecond
    # iterate signal in ms, ith milisecond
    for i in range(30, len(ten) // sr - 30):
        if i % m == 0:
            y[(i - 30) * sr : (i + 30) * sr] = 1
    return y

def simpleFM(T, samples, fc, fm, sr=22050):
    twopi = 2*np.pi

    t = np.linspace(0, T, samples, endpoint=False) # time variable

    # Produce ramp from 0 to 1
    beta = np.linspace(0, 1, samples)


    output = np.sin(twopi*fc*t + beta*np.sin(twopi*fm*t))
    return output
# returns a generator that yields samples from a ramp function
# x: ramp function of form (start1,end1,interval1,end2,interval2,...endn,intervaln)
# rate: yield the rate-th ms each time
# end: how long of a signal we want, in samples
def line(x, num_splits, sr=22050):
    
    T = 0
    for i in range(2, len(x), 2):
        T += x[i]
    
    increment = T // num_splits
    tempos = np.linspace()
    for i in range(0, len(x) - 2, 3):
        start, end, length = x[i], x[i + 1], x[i + 2] // 1000
        
    
# y_len: length of signal in ms
# m: yields a beat at every m ms
def metro_gen(y_len, m, sr=22050):
    sr = sr // 1000 # samples per milisecond
    # iterate signal in ms, ith milisecond
    i = 0
    while i < y_len * sr - 60 * sr:
        if i % int(m * sr) == 0:
            for j in range(60 * sr):
                yield(1)
            i += 60 * sr
        else:
            yield(0)
            i += 1

# sig_len: length of each signal with tempo t_i, in ms
def construct_signal(ramp, sig_len=1000, sr=22050):
    for i in range(0, len(ramp) - 1, 2):
        tempo, length = ramp[i], ramp[i + 1]
        beat = 60 / tempo * 1000 
        yield from metro_gen(length, beat)

# N: number of sample points
def generate_dataset(N,T=30, tempo_range=(60, 200), t_range=(2, 10), sr=22050):
    for point in range(N):
        t = 0
        generator_input = []
        while t < 30:
            tempo = np.random.randint(tempo_range[0], tempo_range[1])
            interval = np.random.randint(t_range[0], t_range[1])
            generator_input += [tempo, interval * 1000]
            
            t += interval
        gen = construct_signal(generator_input)
        signal = np.array(list(gen), dtype=np.float32)
        signal = signal * simpleFM(len(signal) / sr, len(signal), 220, 1)
        filename = "../dataset/audio/" + str(point) + ".wav"
        sf.write(filename, signal, sr)
        with open('../dataset/labels/' + str(point) + '.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["tempo", "duration"])
            for i in range(0, len(generator_input) - 1, 2):
                writer.writerow([generator_input[i], generator_input[i+1]])

def get_files(directory):
    files = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        
        if not dirnames:
            for filename in filenames:
                new_name = self.filename_to_title(filename)
                if not filename.endswith('.lab') and not filename.endswith('.mp3') and not filename.endswith('m4a'):
                    continue
                song_obj = {
                    "filename": filename,
                    "title": new_name
                }
                if dirpath not in files:
                    files[dirpath] = [song_obj]
                else:
                    files[dirpath].append(song_obj)
    return files
    

def training_csv(filename):
    data = []
    with open(filename, mode='r') as file:
        datareader = csv.reader(file)
        next(datareader)
        for row in datareader:
            tempo, interval = int(row[0]), int(row[1])
            data.append((tempo, interval))
    return data

def training_tempo(filename, sr=22050):
    signal = []
    with open(filename, mode='r') as file:
        datareader = csv.reader(file)
        next(datareader)
        for row in datareader:
            tempo, interval = int(row[0]), int(row[1])
            signal.append((tempo, interval))
    signal = np.array(signal)
    return signal

def test_tempo(y, win_len, sr=22050):
    signal = []
    for tempo in y:
        window = (win_len) * [tempo]
        signal += window
    return signal

def get_error(X, y):
    return mean_squared_error(X[:len(y)], y, squared=False)

