import tkinter as tk
from tkinter import ttk
from time import strftime
from PIL import Image, ImageTk
import os
import pytz
from datetime import datetime
import requests
import threading

# Function to get cities for a given timezone
def get_cities_for_timezone(timezone):
    cities = []
    for city in pytz.timezone(timezone).zone.split():
        cities.append(city.split('/')[-1].replace('_', ' '))
    return cities

# Function to get the weather information for a city
def get_weather(city):
    api_key = 'cff24430cafc071bd92b2ec247332ffe'  # Replace with your OpenWeatherMap API key
    current_weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    try:
        response = requests.get(current_weather_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        weather_data = response.json()

        if "main" in weather_data:
            main = weather_data["main"]
            temperature = main["temp"]
            weather_desc = weather_data["weather"][0]["description"]
            weather_info = f"Temp: {temperature}°C\n{weather_desc.title()}"
        else:
            weather_info = "Weather data not available"

    except requests.exceptions.HTTPError as http_err:
        weather_info = f"HTTP error: {http_err}"
    except Exception as err:
        weather_info = f"Error: {err}"

    return weather_info

# Function to update the time and weather
def update_time_and_weather():
    # Update time
    selected_timezone = timezone_var.get()
    if selected_timezone:
        try:
            timezone = pytz.timezone(selected_timezone)
        except pytz.UnknownTimeZoneError:
            timezone = None
    else:
        timezone = None

    if timezone:
        current_time = datetime.now(timezone)
    else:
        current_time = datetime.now()

    # Format the time string
    time_string = current_time.strftime('%H:%M:%S %p')
    date_string = current_time.strftime('%Y-%m-%d')
    label.config(text=time_string)
    date_label.config(text=date_string)
    label.after(1000, update_time_and_weather)

    # Change background based on time of day
    hour = current_time.hour
    if 6 <= hour < 12:
        background_image = Image.open(morning_path)
    elif 12 <= hour < 18:
        background_image = Image.open(afternoon_path)
    elif 18 <= hour < 24:
        background_image = Image.open(evening_path)
    else:
        background_image = Image.open(night_path)

    # Resize the image to fit the window
    background_image = background_image.resize((root.winfo_width(), root.winfo_height()), Image.LANCZOS)
    background_image = ImageTk.PhotoImage(background_image)

    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    canvas.image = background_image  # Keep a reference to avoid garbage collection

    # Update city dropdown based on selected timezone
    if timezone:
        suggested_cities = get_cities_for_timezone(selected_timezone)
        city_dropdown['values'] = suggested_cities
    else:
        city_dropdown['values'] = []

# Function to update the weather information in a separate thread
def update_weather():
    selected_city = city_var.get()
    if selected_city:
        weather_info = get_weather(selected_city)
    else:
        weather_info = "Select a city to see weather"
    weather_label.config(text=weather_info)

# Callback for when the city is selected
def on_city_select(event):
    threading.Thread(target=update_weather).start()

# Get absolute paths of images
script_dir = os.path.dirname(os.path.abspath(__file__))
morning_path = os.path.join(script_dir, 'morning.jpg')
afternoon_path = os.path.join(script_dir, 'afternoon.jpg')
evening_path = os.path.join(script_dir, 'evening.jpg')
night_path = os.path.join(script_dir, 'night.jpg')

# Create main window
root = tk.Tk()
root.title('Clock')
root.geometry('800x600')

# Set up canvas for background image
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(fill='both', expand=True)

# Add label to display date
date_label = tk.Label(root, font=('calibri', 20, 'bold'), background='white', foreground='black')
date_label.place(relx=0.5, rely=0.3, anchor='center')

# Add label to display time
label = tk.Label(root, font=('calibri', 40, 'bold'), background='white', foreground='black')
label.place(relx=0.5, rely=0.4, anchor='center')

# Add label to display weather
weather_label = tk.Label(root, font=('calibri', 20, 'bold'), background='white', foreground='black')
weather_label.place(relx=0.5, rely=0.5, anchor='center')

# Create a frame for dropdown menu
timezone_frame = tk.Frame(root, bg='lightgrey')
timezone_frame.place(relx=0.5, rely=0.65, anchor='center')

# Add title for the timezone dropdown
timezone_title = tk.Label(timezone_frame, text="Time Zones", font=('calibri', 12, 'bold'), bg='lightgrey')
timezone_title.pack(side='top', anchor='center')

# Create a dropdown menu for time zones
timezone_var = tk.StringVar()
timezone_dropdown = ttk.Combobox(timezone_frame, textvariable=timezone_var, state='readonly')
timezone_dropdown['values'] = pytz.all_timezones
timezone_dropdown.pack(side='top', anchor='center')

# Add title for the city dropdown
city_title = tk.Label(timezone_frame, text="Select City", font=('calibri', 12, 'bold'), bg='lightgrey')
city_title.pack(side='top', anchor='center')

# Create a dropdown menu for cities
city_var = tk.StringVar()
city_dropdown = ttk.Combobox(timezone_frame, textvariable=city_var, state='readonly')
city_dropdown.pack(side='top', anchor='center')
city_dropdown.bind("<<ComboboxSelected>>", on_city_select)

# Bind the update_time_and_weather function to timezone_var change
timezone_var.trace('w', lambda *args: update_time_and_weather())

# Initialize the time and weather function
update_time_and_weather()

# Run the main event loop
root.mainloop()
