
import FreeSimpleGUI as sg
import requests
from io import BytesIO
from PIL import Image


def show_weather_window():
    API_KEY = "a84ca0a16d8f78e5f7ba392c03cd6ffd"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"

    # GUI layout
    layout = [
        [sg.Text("Enter City:"), sg.InputText(key="CITY")],
        [sg.Button("Get Weather"), sg.Button("Exit")],
        [sg.Image(key="ICON")],
        [sg.Text(size=(40, 1), key="RESULT")],
        [sg.Text(size=(40, 1), key="TEMP")],
        [sg.Text(size=(40, 1), key="HUMIDITY")],
        [sg.Text(size=(40, 1), key="DESCRIPTION")],
    ]

    # Create window
    window = sg.Window("Weather App with Icons", layout, font=("Arial", 17))

    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        if event == "Get Weather":
            city = values["CITY"]
            if not city:
                window["RESULT"].update("Please enter a city name.")
                continue

            params = {"q": city, "appid": API_KEY, "units": "metric"}
            try:
                response = requests.get(BASE_URL, params=params)
                data = response.json()

                if data["cod"] == 200:
                    temp = data["main"]["temp"]
                    humidity = data["main"]["humidity"]
                    desc = data["weather"][0]["description"]
                    icon_code = data["weather"][0]["icon"]

                    # Download and display the icon
                    icon_response = requests.get(ICON_URL.format(icon_code))
                    img = Image.open(BytesIO(icon_response.content))
                    bio = BytesIO()
                    img.save(bio, format="PNG")
                    window["ICON"].update(data=bio.getvalue())

                    window["RESULT"].update(f"Weather for {city.capitalize()}:")
                    window["TEMP"].update(f"Temperature: {temp}°C")
                    window["HUMIDITY"].update(f"Humidity: {humidity}%")
                    window["DESCRIPTION"].update(f"Condition: {desc.capitalize()}")
                else:
                    window["RESULT"].update("City not found.")
                    window["TEMP"].update("")
                    window["HUMIDITY"].update("")
                    window["DESCRIPTION"].update("")
                    window["ICON"].update(data=None)

            except Exception as e:
                window["RESULT"].update("Error fetching data.")
                window["TEMP"].update("")
                window["HUMIDITY"].update("")
                window["DESCRIPTION"].update("")
                window["ICON"].update(data=None)

    window.close()
