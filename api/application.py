from tempo import Tempo
from volume import Volume
from db import Database
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect#, join_room, leave_room, close_room, rooms

import numpy as np
from collections import OrderedDict
import sys
import math

import statistics
import librosa


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the applicationlication to choose
# the best option based on installed packages.
async_mode = None

application = Flask(__name__, static_folder='../build', static_url_path='/')
application.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(application, logger=True, binary=True, cors_allowed_origins="*")

tempo_obj = Tempo()
volume_obj = Volume()
database = Database()

def load_song(path_to, win_len=10):
    x, sr = librosa.load(path_to)
    win = sr * win_len
    lx = len(x)
    xp_len = int(np.ceil(lx/win)) * win
    x.resize(xp_len)
    x_chunks = x.reshape((len(x) // (sr * win_len), (sr * win_len)))
    return x_chunks

def precompute_t_v(x_chunks, sr=22050):
    tempos, volumes = [], []
    for xc in x_chunks:
        tempos.append(np.floor(tempo_obj.global_tempo(xc, sr)))
        volumes.append(volume_obj.get_average_power(xc, sr))
    return tempos, volumes

def get_songs():
    widmung = load_song('./db/widmung/trifonov.mp3')
    desabends = load_song('./db/desabends/rec1.mp3')
    scriabin_etude_op_42_no_5 = load_song('./db/scriabin_etude1/1.mp3')

    print("songs loaded!")
    return widmung, desabends, scriabin_etude_op_42_no_5

one, two, three = get_songs()
songs_mapping = {
    "widmung" : precompute_t_v(one),
    "desabends" : precompute_t_v(two),
    "etude" : precompute_t_v(three)
}

@application.route('/')
def index():
    return application.send_static_file('index.html')

@socketio.on('connect', namespace="/test")
def connect():
    session['global_audio'] = []
    session['local_audio'] = []
    emit('server_response', {'data': 'connected'})

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate
    session['win_index'] = 0

@socketio.on('send_audio', namespace="/test")
def print_message(audio):
    audio = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['local_audio'] += audio
    session['global_audio'] += audio

@socketio.on('tempo', namespace="/test")
def tempo(song, local=False):
    sr, p_sr = session['sample_rate'], 22050
    print("tempo")
    if local:
        # my_audio = np.array(session['local_audio'], np.float32)

        # Professional Recording signal
        index = session['win_index']
        if (index + 1) < len(songs_mapping[song][0]):
            session['win_index'] += 1
    else:
        my_audio = np.array(session['global_audio'], np.float32)
        perf_audio = songs_mapping[song]

    # live audio tempo and volume
    # tempo = math.floor(tempo_obj.global_tempo(my_audio, sr))
    # avg_power = volume_obj.get_average_power(my_audio, sr)

    p_tempo = songs_mapping[song][0][index]
    p_avg_power = songs_mapping[song][1][index]

    session['local_audio'] = []
    if local:
        emit('output local tempo', {'p_tempo' : p_tempo, 'p_volume' : p_avg_power})
    # else:
    #     emit('output global tempo', {'tempo' : tempo, 'volume' : volume})
    #     session['global_audio'] = []


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print("disconnect")
    session['global_audio'] = []
    session['local_audio'] = []
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(application, debug=True, host='0.0.0.0', port=5000)