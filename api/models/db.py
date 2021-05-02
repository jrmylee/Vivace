from pymongo import MongoClient
import librosa
import csv
from tempo import overlap_windowed_tempo
from volume import overlap_windowed_volume

client = MongoClient('localhost', 27017)
db = client['vivace_db']

rows = []
with open("./db/db.csv", 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        rows.append({
            'title': row[0],
            'composer': row[1], 
            'performer': row[2],
            'path' : 'db/' + row[0].lower().replace(" ", "_") + '/' + row[2].lower() + ".mp3"
        })
def get_songs():
    return rows

def precompute_t_v(signal, sr=22050):
    tempos = overlap_windowed_tempo(signal)
    volumes = overlap_windowed_volume(signal)

    return tempos, volumes

def push_to_db():
    songs = {}
    performances = db.performances
    for song_data in get_songs():
        song, sr = librosa.load(song_data['path'])
        tempos, volumes = precompute_t_v(song)
        print(song_data['performer'] + ": " + song_data['title'])
        title, performer = song_data['title'], song_data['performer']

        performance = {
            "title" : title,
            "performer" : performer,
            "tempos" : tempos,
            "volumes" : volumes
        }
        perf_id = performances.insert_one(performance).inserted_id
        print(perf_id)
    return songs

songs_mapping = push_to_db()