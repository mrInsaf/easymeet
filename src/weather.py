import os
import requests

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather_by_coordinates(coordinates):
    url = f"https://api.openweathermap.org/data/2.5/weather?" \
          f"lat={coordinates[0]}" \
          f"&lon={coordinates[1]}" \
          f"&appid={API_KEY}" \
          f"&units=metric" \
          f"&lang=ru"

    request = requests.get(url)
    if request.status_code != 200:
        return
    weather = request.json()
    result = dict()
    result['temp'] = weather['main']['temp']
    result['temp_feels'] = weather['main']['feels_like']
    result['pressure'] = weather['main']['pressure']
    result['wind_speed'] = weather['wind']['speed']
    result['weather'] = weather['weather'][0]['description']
    return result
