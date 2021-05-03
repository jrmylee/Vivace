import librosa
import numpy as np

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