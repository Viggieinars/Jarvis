import requests
import os

def get_weather(city):
    openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The current weather in {city} is {weather} with a temperature of {temperature}°C."
    else:
        return "I'm sorry, I couldn't get the weather information right now."
