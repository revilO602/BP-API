import googlemaps
from bpproject.settings import GOOGLE_API_KEY

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


def get_distance(origin_id, destination_id):
    result = gmaps.distance_matrix(f'place_id:{origin_id}',
                                   f'place_id:{destination_id}')
    print(result)
    distance = result["rows"][0]["elements"][0]["distance"]  # in meters
    duration = result["rows"][0]["elements"][0]["duration"]  # in seconds
    return distance, duration
