from tempo import Tempo
from volume import Volume
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
socketio = SocketIO(application, binary=True, cors_allowed_origins="*")

tempo_obj = Tempo()
volume_obj = Volume()

@application.route('/')
def index():
    return application.send_static_file('index.html')

@socketio.on('connect', namespace="/test")
def connect():
    print("connect");
    session['global_audio'] = []
    session['local_audio'] = []
    emit('server_response', {'data': 'connected'})

@socketio.on('piece', namespace="/test")
def piece(str):
    print("setting piece")
    piece, sr = librosa.load(f'./db/{str}.mp3')
    session['performance'] = piece
    session['window'] = {
        'start' : 0,
        'end' : 3,
        'sr' : 22050
    }

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate
    # send some message to front
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': "sampleRate : %s" % sampleRate, 'count': session['receive_count'] })

## If we wanted to create a new websocket endpoint,
## use this decorator, passing in the name of the
## event we wish to listen out for
@socketio.on('message', namespace="/test")
def print_message(audio):
    ## When we receive a new event of type
    ## 'message' through a socket.io connection
    ## we print the socket ID and the message
    # tempo_obj.process(message)
    audio = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['local_audio'] += audio
    session['global_audio'] += audio

@socketio.on('tempo', namespace="/test")
def tempo(local=False):
    sr = session['sample_rate']
    print("tempo")
    if local:
        my_audio = np.array(session['local_audio'], np.float32)
        perf_audio = session['performance']
        start, end, rate = session['window']['start'], session['window']['end'], session['window']['sr']
        perf_audio = perf_audio[start * rate : end * rate]

        if (end + 3) * rate < len(session['performance']):
            session['window']['start'] += 3
            session['window']['end'] += 3
    else:
        my_audio = np.array(session['global_audio'], np.float32)
        perf_audio = session['performance']

    # live audio tempo and volume
    tempo = math.floor(tempo_obj.global_tempo(my_audio, sr))
    spec = volume_obj.compute_power_dB(my_audio, sr)
    spec = spec[spec > -1000]
    mean_vol = statistics.mean(spec)
    volume = math.floor(mean_vol)

    p_tempo = math.floor(tempo_obj.global_tempo(perf_audio, sr))
    p_spec = volume_obj.compute_power_dB(perf_audio, sr)
    p_spec = p_spec[p_spec > -1000]
    p_mean_vol = statistics.mean(p_spec)
    p_volume = math.floor(p_mean_vol)

    session['local_audio'] = []
    if local:
        emit('output local tempo', {'tempo' : tempo, 'volume' : volume, 'p_tempo' : p_tempo, 'p_volume' : p_volume})
    else:
        emit('output global tempo', {'tempo' : tempo, 'volume' : volume})
        session['global_audio'] = []


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print("disconnect")
    #my_audio = np.array(session['audio'], np.float32)
    #scipy.io.wavfile.write('out.wav', 44100, my_audio.view('int16'))
    #print(my_audio.view('int16'))

    # https://stackoverflow.com/a/18644461/466693
    session['global_audio'] = []
    session['local_audio'] = []
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(application, debug=False)