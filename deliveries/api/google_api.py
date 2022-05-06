import googlemaps
from bpproject.settings import GOOGLE_API_KEY

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


def get_distance(origin_id, destination_id):
    """
    Retrieve route distance and expected duration for cars from the Google Maps API.

    :param origin_id: Google place ID of the starting location
    :param destination_id: Google place ID of the end location
    :return: tuple of distance and duration objects with numerical and string representations
    """
    result = gmaps.distance_matrix(f'place_id:{origin_id}',
                                   f'place_id:{destination_id}')
    distance = result["rows"][0]["elements"][0]["distance"]  # in meters
    duration = result["rows"][0]["elements"][0]["duration"]  # in seconds
    return distance, duration


def get_distance_for_sort(delivery_obj, latitude, longitude):
    """
    Get route distance between courier coordinates and pickup_place for the purpose of sorting close deliveries.

    :param delivery_obj: Delivery object
    :return: route distance for driving between coordinates and pick up place of delivery - positive integer in meters
    """
    origin = {
        "lat": latitude,
        "lng": longitude
    }
    result = gmaps.distance_matrix(origin,
                                   f'place_id:{delivery_obj.pickup_place.place_id}')
    print(result)
    distance = result["rows"][0]["elements"][0]["distance"]["value"]  # in meters
    return distance
