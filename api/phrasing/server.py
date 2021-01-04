from flask import Flask
import phrase
import sys
import librosa
from flask_cors import CORS

sys.path.append("/Users/jrmylee/Documents/dev/projects/mir/repos/tempo-cnn")

from tempocnn.feature import read_features

app = Flask(__name__)
CORS(app)

@app.route("/phrases/<song>/<id>")
def phrases(song, id):
    values, phrases = phrase.get_phrases(f'recordings/{song}/{id}.csv', 1.486077097505669)
    return {
        "phrases" : phrases
    }

@app.route("/phrases-array/<song>/<id>")
def phrases_array(song, id):
    x, sr = librosa.load(f'recordings/{song}/{id}.mp3')
    p, phrases = phrase.get_phrases_onsets(x)
    print(phrases)
    return {
        "phrases" : phrases
    }

if __name__ == "__main__":
    app.run()
