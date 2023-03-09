from config import GEO_API_KEY
import requests
import json


def get_data_by_coordinates(departure: tuple, arrive: tuple, mode: str = "jam"):
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
    result = None
    try:
        result = request.json()
    except Exception as ex:
        result = {'error': ex}
    finally:
        return result
