from tempo import Tempo
from volume import Volume
from db import Database
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect#, join_room, leave_room, close_room, rooms
from flask_cors import CORS, cross_origin

import numpy as np
from collections import OrderedDict
import math
from scipy.signal import medfilt

import statistics
import librosa
import csv

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the applicationlication to choose
# the best option based on installed packages.
async_mode = None

application = Flask(__name__, static_folder='../build', static_url_path='/')
application.config['SECRET_KEY'] = 'secret!'
cors = CORS(application)
application.config['CORS_HEADERS'] = "Content-Type"

socketio = SocketIO(application, logger=True, binary=True, cors_allowed_origins="*")

tempo_obj = Tempo()
volume_obj = Volume()
database = Database()

def load_song(path_to, win_len=3):
    x, sr = librosa.load(path_to)
    win = sr * win_len
    lx = len(x)
    xp_len = int(np.ceil(lx/win)) * win
    x.resize(xp_len)
    x_chunks = x.reshape((len(x) // (sr * win_len), (sr * win_len)))
    return x_chunks

# def precompute_t_v(x_chunks, sr=22050):
#     tempos, volumes = [], []
#     tempo, volume = [], []
#     for xc in x_chunks:
#         tempo.append(np.floor(tempo_obj.global_tempo(xc, sr)))
#         volume.append(volume_obj.get_average_power(xc, sr))

#         if len(tempo) == 3:
#             tempos.append(medfilt(tempo)[1])
#             volumes.append(medfilt(volume)[1])
#             tempo, volume = [], []

#     return tempos, volumes

def precompute_t_v(signal, sr=22050):
    tempos = tempo_obj.overlap_windowed_tempo(signal)
    volumes = volume_obj.overlap_windowed_volume(signal)

    return tempos, volumes


# returns tempo-volume data for songs in db
# def get_songs_from_db():
#     songs = {}
#     for song_data in database.get_songs():
#         song = load_song(song_data['path'], win_len=1)
#         tv = precompute_t_v(song)
#         if song_data['title'] in songs:
#             songs[song_data['title']][song_data['performer']] = tv
#         else:
#             songs[song_data['title']] = {
#                 song_data['performer']: tv
#             }
#     print(songs)
#     return songs

def get_songs_from_db():
    songs = {}
    for song_data in database.get_songs():
        song, sr = librosa.load(song_data['path'])
        tv = precompute_t_v(song)
        print(song_data['performer'] + ": " + song_data['title'])
        if song_data['title'] in songs:
            songs[song_data['title']][song_data['performer']] = tv
        else:
            songs[song_data['title']] = {
                song_data['performer']: tv
            }
    return songs

songs_mapping = get_songs_from_db()

@application.route('/')
def index():
    return application.send_static_file('index.html')

@application.route('/songs')
@cross_origin()
def songs():
    songs = {}
    with open('db/db.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            songs[row[0]] = {
                'title': row[0],
                'composer': row[1], 
                'perfomer': row[2],
                'path' : 'db/' + row[0].lower().replace(" ", "_") + '/' + row[2].lower() + ".mp3"
            }
    return songs

@socketio.on('connect', namespace="/test")
def connect():
    session['local_tempos'] = []
    session['local_volumes'] = []
    emit('server_response', {'data': 'connected'})

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate
    session['local_audio'] = np.zeros(sampleRate * 2, np.float32)
    session['win_index'] = 0

@socketio.on('send_audio', namespace="/test")
def print_message(audio):
    audio = list(OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values())
    session['local_audio'] = np.append(session['local_audio'], audio)

# overlapping windows
@socketio.on('tempo', namespace="/test")
def tempo(song, local=False):
    sr, p_sr = session['sample_rate'], 22050

    # Professional Recording signal
    # index = session['win_index']
    # if (index + 1) < len(songs_mapping[song][0]):
    #     session['win_index'] += 1

    # live audio tempo and volume
    tempo = math.floor(tempo_obj.global_tempo(session['local_audio'], sr))
    avg_power = volume_obj.get_average_power(session['local_audio'], sr)

    p_tempos = {}
    p_volumes = {}

        # Professional Recording signal
    index = session['win_index']
    first_key = list(songs_mapping[song].keys())[0]
    if (index + 1) < len(songs_mapping[song][first_key][0]):
        session['win_index'] += 1

    for performance in songs_mapping[song]:
        p_tempos[performance] = songs_mapping[song][performance][0][index]
        p_volumes[performance] = songs_mapping[song][performance][1][index]

    # pop first 1 second from audio 
    session['local_audio'] = session['local_audio'][sr * 1 : ]
    if local:
        emit('output local tempo', {
            'tempo' : tempo,
            'volume' : avg_power,
            'p_tempo' : p_tempos, 
            'p_volume' : p_volumes
        })
    # else:
    #     emit('output global tempo', {'tempo' : tempo, 'volume' : volume})
    #     session['global_audio'] = []


# Median Filtered
# # called every 1 second by the front end
# @socketio.on('tempo', namespace="/test")
# def tempo(song, local=False):
#     sr = session['sample_rate']
#     audio = np.array(session['local_audio'])

#     tempo = math.floor(tempo_obj.global_tempo(audio, sr))
#     power = volume_obj.get_average_power(audio, sr)
#     session['local_tempos'].append(tempo)
#     session['local_volumes'].append(power)

#     if len(session['local_tempos']) == 3:
#         median_tempo = medfilt(session['local_tempos'])[1]
#         median_volume = medfilt(session['local_volumes'])[1]
#         session['local_tempos'], session['local_volumes'] = [], []

#         p_tempos = {}
#         p_volumes = {}

#         # Professional Recording signal
#         index = session['win_index']
#         first_key = list(songs_mapping[song].keys())[0]
#         if (index + 1) < len(songs_mapping[song][first_key][0]):
#             session['win_index'] += 1

#         for performance in songs_mapping[song]:
#             p_tempos[performance] = songs_mapping[song][performance][0][index]
#             p_volumes[performance] = songs_mapping[song][performance][1][index]

#         session['local_audio'] = []
#         emit('output local tempo', {
#             'tempo' : median_tempo,
#             'volume' : median_volume,
#             'p_tempos' : p_tempos, 
#             'p_volumes' : p_volumes
#         })


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print("disconnect")
    session['global_audio'] = []
    session['local_audio'] = []
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(application, debug=True, host='0.0.0.0', port=5000)