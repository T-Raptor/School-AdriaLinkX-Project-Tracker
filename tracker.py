import requests
import random
import time
import json
PATH_CONFIG = "config.json"
WARNINGS = [
    "Ongoing standstorm",
    "Extreme weather",
    "Acid rain",
    "Maintenance"
]


#================================================
#================================================


def get_config_url():
    with open(PATH_CONFIG) as h:
        return json.load(h)["url"]
URL_API = get_config_url()


def register_shuttle(serial):
    rsp = requests.post(URL_API + "/shuttles", json={"serial": serial})
    report_failure(rsp)
    return rsp.json()


def fetch_tracks():
    rsp = requests.get(URL_API + "/tracks")
    report_failure(rsp)
    return rsp.json()


cache_tracks = None
def get_tracks():
    global cache_tracks
    if cache_tracks == None:
        cache_tracks = fetch_tracks()
    return cache_tracks


def report_failure(rsp):
    if rsp.status_code < 200 or rsp.status_code >= 300:
        print(rsp.content)
        raise RuntimeError("Request failure")


def push_shuttle_move(shuttle):
    pos = calculate_position(shuttle["path"])
    event = {
        "target": shuttle["id"],
        "subject": "MOVE",
        "moment": int(time.time() * 1000),
        "latitude": pos["latitude"],
        "longitude": pos["longitude"]
    }
    rsp = requests.post(URL_API + "/events", json=event)
    report_failure(rsp)
    return rsp


def push_warning(track_id, reason):
    event = {
        "target": track_id,
        "subject": "WARN",
        "moment": int(time.time() * 1000),
        "reason": reason
    }
    rsp = requests.post(URL_API + "/events", json=event)
    report_failure(rsp)
    return rsp


#================================================
#================================================


def random_entry(array):
    return array[random.randint(0, len(array)-1)]


def random_track():
    return random_entry(get_tracks())


def get_available_tracks(station):
    return [track for track in get_tracks() if track["station1"]["id"] == station["id"] or track["station2"]["id"] == station["id"]]


def is_track_taken(track, shuttles):
    s1 = track["station1"]
    s2 = track["station2"]
    for shuttle in shuttles:
        if "path" in shuttle:
            path = shuttle["path"]
            if path["progress"] < 1.0 and (path["start"] == s1 or path["start"] == s2) and (path["stop"] == s1 or path["stop"] == s2):
                return True
    return False


def track_to_path(track, station_start):
    station_stop = track["station2"] if track["station1"]["id"] == station_start["id"] else track["station1"]
    return create_path(station_start, station_stop)


def random_station(tracks = None):
    if tracks == None:
        tracks = get_tracks()
    track = random_entry(tracks)
    return random_entry([track["station1"], track["station2"]])


def random_serial():
    def random_serial_group(size):
        return ''.join([random_entry("0123456789ABCDEF") for i in range(size)])
    return f"{random_serial_group(4)}-{random_serial_group(4)}-{random_serial_group(4)}"


#================================================
#================================================


def create_path(station_start, station_stop):
    return {
        "start": station_start,
        "stop": station_stop,
        "progress": 0
    }


def calculate_position(path):
    lat_start = path["start"]["latitude"]
    lon_start = path["start"]["longitude"]
    lat_stop = path["stop"]["latitude"]
    lon_stop = path["stop"]["longitude"]
    lat_diff = lat_stop - lat_start
    lon_diff = lon_stop - lon_start
    return {"longitude": lat_start + lat_diff * path["progress"], "latitude": lon_start + lon_diff * path["progress"]}


def all_except(array, exception):
    return [entry for entry in array if entry != exception]


#================================================
#================================================


WARNING_RATIO = 0.1
def update_warnings():
    if random.random() < WARNING_RATIO:
        track = random_track()
        push_warning(track["id"], random_entry(WARNINGS))



def update_shuttle(shuttle, shuttles):
    if "path" not in shuttle:
        track = random_track()
        if is_track_taken(track, shuttles):
            return
        shuttle["path"] = create_path(track["station1"], track["station2"])
    path = shuttle["path"]
    if path["progress"] > 1:
        tracks = get_available_tracks(path["stop"])
        track = random_entry(tracks)
        if not is_track_taken(track, all_except(shuttles, shuttle)):
            path = track_to_path(track, path["stop"])
            shuttle["path"] = path
    else:
        path["progress"] += 0.02
    time.sleep(random.random() * .5)
    push_shuttle_move(shuttle)


def update_shuttles(shuttles):
    for shuttle in shuttles:
        update_shuttle(shuttle, shuttles)


def mainloop(shuttles):
    while True:
        update_shuttles(shuttles)
        update_warnings()
        time.sleep(1)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--count", "-c", default=1, type=int)
    
    args = parser.parse_args()
    count = args.count

    shuttles = []
    for i in range(count):
        shuttles.append(register_shuttle(random_serial()))
    print(f"Simulating {count} shuttle(s)...")
    mainloop(shuttles)