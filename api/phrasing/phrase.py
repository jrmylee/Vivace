import squares
import csv
import numpy as np
import librosa

def parse_tempo_csv(filename):
    tempo_arr = []
    with open(filename) as csvfile:
        temporeader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        temporeader = list(temporeader)[1:]
        last_tempo, start = None, None
        for row in temporeader:
            tempo_predictions = row[0].split(',')
            last_tempo = np.argmax(tempo_predictions)
            offset = 30
            tempo_arr.append(last_tempo + offset)
    return tempo_arr

# returns (points, phrase boundaries)
def get_phrases(filename, period, original=False):
    t2 = parse_tempo_csv(filename)
    xt2 = np.arange(len(t2))

    xt2_fitted, xt2_phrases = squares.segls(len(t2), xt2, t2, 4)    
    return xt2_fitted, [(a[0] * period, a[1] * period) for a in xt2_phrases]

def moving_avg(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def get_phrases_array(array, period, cost=1):
    rms = librosa.feature.rms(array, hop_length=22050)
    rms_smooth = moving_avg(rms[0], 5)
    xt2 = np.arange(len(rms_smooth))
    xt2_fitted, xt2_phrases = squares.segls(len(rms_smooth), xt2, rms_smooth, cost)
    return xt2_fitted, [(a[0] * period, a[1] * period) for a in xt2_phrases]

def get_phrases_onsets(arr):
    onsets = librosa.onset.onset_detect(arr)
    od = np.gradient(onsets)
    smooth = moving_avg(od, 10)
    return squares.segls(len(smooth), np.arange(len(smooth)), smooth, 4)
