import requests
import os
import json
import random
URL_API = "http://localhost:8080/api"


def random_entry(array):
    return array[random.randint(0, len(array)-1)]


def create_shuttle(serial, station_start):
    return {
        "serial": serial,
        "latitude": station_start["latitude"],
        "longitude": station_start["longitude"]
    }


def random_station(tracks = None):
    if tracks == None:
        tracks = get_tracks()
    track = random_entry(tracks)
    return random_entry([track["station1"], track["station2"]])


def random_serial():
    def random_serial_group(size):
        return ''.join([random_entry("0123456789ABCDEF") for i in range(size)])
    return f"{random_serial_group(4)}-{random_serial_group(4)}-{random_serial_group(4)}"


def create_random_shuttle():
    serial = random_serial()
    station = random_station()
    return create_shuttle(serial, station)


def fetch_tracks():
    rsp = requests.get(os.path.join(URL_API, "tracks"))
    return rsp.json()


cache_tracks = None
def get_tracks():
    global cache_tracks
    if cache_tracks == None:
        cache_tracks = fetch_tracks()
    return cache_tracks



tracks = get_tracks()
shuttle = create_random_shuttle()
print(shuttle)