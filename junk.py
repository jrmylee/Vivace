
def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def get_env(x):
    return librosa.beat.tempo(onset_envelope=x)[0]
            
def get_bpm(timing_data):
    piece_length = math.floor(timing_data[len(timing_data) - 1])
    num_samples = 22050 * piece_length
    onset_env = np.zeros(num_samples + 1)
    for point in timing_data:
        point = math.floor(point) * 22050
        onset_env[point] = 1
    
    points = [onset_env[i: i + 22050] for i in range(0, len(onset_env), 22050)]
    with Pool(cpu_count()) as p:
        tempos = p.map(get_env, points)
    bpm = statistics.mean(
        tempos
    )
    print(bpm)
    return bpm

# Processes single piece
# params: timing, dynamics, path to timing and dynamics files resp
# returns average tempo, average volume for each piece
# in form (pid, tempo, volume)
def compute_feature(timing, dynamics):
    t, d = pd.read_csv(timing), pd.read_csv(dynamics)
    columns = t.columns
    ret = []
    for column in columns:
        if not column.startswith("pid"):
            continue
        prefix = timing[:timing.rindex("time")]
        dyn = prefix + "dynNORM.csv"
        timing_data, dyn_data = t[column], d[column]
        print(column + " processing bpm")
        avg_bpm = get_bpm(timing_data)
        dyn_mean = dyn_data.mean()
        ret.append((column, avg_bpm, dyn_mean))
    return np.array(ret)
        

def create_db():
    db = []
    timing_path = "csvs/beat_time/"
    dynamics_path = "csvs/beat_dyn/"
    
    timings =  list(listdir_nohidden(timing_path))
    dynamics = list(listdir_nohidden(dynamics_path))
    timings.sort()
    dynamics.sort()
    num_pieces = len(timings)
    
    ret = {}
    for i in range(num_pieces):
        timing_name, dyn_name = timings[i], dynamics[i]
        piece_name = timing_name[:timing_name.rindex("beat")]        
        tp, dp = os.path.join(timing_path, timing_name), os.path.join(dynamics_path, dyn_name)
        ret[piece_name] = compute_feature(tp, dp)
    return ret 


if __name__ == "__main__":
    db = create_db()
