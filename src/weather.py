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
    result = f"Температура: {weather['main']['temp']}°C\n" \
             f"Ощущается как: {weather['main']['feels_like']}°C\n" \
             f"Вероятность осадков: {weather['main']['humidity']}%\n" \
             f"Давление: {weather['main']['pressure']}мм рт. ст.\n" \
             f"Скорость ветра: {weather['wind']['speed']}м/с\n" \
             f"На небе {weather['weather'][0]['description']}"
    return result
