from tempo import Tempo
from volume import Volume
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect#, join_room, leave_room, close_room, rooms
from flask_cors import CORS, cross_origin

import numpy as np
from collections import OrderedDict
import math
from scipy.signal import medfilt

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['vivace_db']

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

@application.route('/')
def index():
    return application.send_static_file('index.html')

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
    session['win_index'] += 1

    for performance in db.performances.find({"title" : song}):
        if index < len(performance["tempos"]):
            performer = performance["performer"]
            p_tempos[performer] = performance["tempos"][index]
            p_volumes[performer] = performance["volumes"][index]

    print(p_tempos, p_volumes)
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