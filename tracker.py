import requests
import os
import json
URL_API = "http://localhost:8080/api"


def fetch_tracks():
    rsp = requests.get(os.path.join(URL_API, "tracks"))
    return rsp.json()


cache_tracks = None
def get_tracks():
    global cache_tracks
    if cache_tracks == None:
        cache_tracks = fetch_tracks()
    return cache_tracks


print(get_tracks())