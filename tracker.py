import requests
import os
import json
import random
import time
URL_API = "http://localhost:8080/api"


def random_entry(array):
    return array[random.randint(0, len(array)-1)]


def register_shuttle(serial):
    return {
        "serial": serial,
        "id": 9
    }


def create_shuttle(serial, station_start):
    shuttle = register_shuttle(serial)
    shuttle["latitude"] = station_start["latitude"]
    shuttle["longitude"] = station_start["latitude"]
    return shuttle


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
    event = {
        "target": shuttle["id"],
        "subject": "MOVE",
        "moment": int(time.time() * 1000),
        "latitude": shuttle["latitude"],
        "longitude": shuttle["longitude"]
    }
    rsp = requests.post(os.path.join(URL_API, "events"), json=event)
    report_failure(rsp)
    return rsp



tracks = get_tracks()
shuttle = create_random_shuttle()
push_shuttle_move(shuttle)
print(shuttle)