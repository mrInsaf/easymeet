import os
import requests
import json
import logging
from geopy.geocoders import Nominatim

geo_locator = Nominatim(user_agent="EasyMeet")

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

GEO_API_KEY = os.getenv("GEO_API_KEY")


def get_coordinates_by_address(address: str):
    location = None
    try:
        location = geo_locator.geocode(address)
    except Exception as ex:
        logger.warning(ex)
    return location.latitude, location.longitude


def get_data_by_coordinates(departure: tuple, arrive: tuple, mode: str = "jam"):
    if mode == "test":
        return 1319, 111287
    url = f'https://routing.api.2gis.com/get_dist_matrix?key={GEO_API_KEY}&version=2.0'
    headers = {'Content-type': 'application/json'}
    data = {
        "points": [
            {
                "lat": departure[0],
                "lon": departure[1]
            },
            {
                "lat": arrive[0],
                "lon": arrive[1]
            }
        ],
        "sources": [0],
        "targets": [1],
        "type": mode,
    }
    request = requests.post(url, data=json.dumps(data), headers=headers)
    try:
        data = request.json()
        return data["routes"][0]["duration"], data["routes"][0]["distance"]
    except Exception as ex:
        logger.warning(ex)
