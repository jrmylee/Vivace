from tempo import Tempo
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect#, join_room, leave_room, close_room, rooms

import scipy.io.wavfile
import numpy as np
from collections import OrderedDict
import sys
import math
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, binary=True, cors_allowed_origins="*")

tempo_obj = Tempo()

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace="/test")
def connect():
    print("connect");
    session['global_audio'] = []
    session['local_audio'] = []
    emit('server_response', {'data': 'connected'})

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
    values = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['local_audio'] += values
    session['global_audio'] += values

@socketio.on('tempo', namespace="/test")
def tempo(local=False):
    sr = session['sample_rate']

    if local:
        my_audio = np.array(session['local_audio'], np.float32)
    else:
        my_audio = np.array(session['global_audio'], np.float32)

    tempo = math.floor(tempo_obj.global_tempo(my_audio, sr))
    session['local_audio'] = []
    if local:
        emit('output local tempo', {'tempo' : tempo})
    else:
        emit('output global tempo', {'tempo' : tempo})
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
    socketio.run(app, debug=False)