#!/usr/bin/env python

import time
import sys
import requests
from datetime import datetime
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# Configuration for the matrix
def configure_matrix():
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.gpio_slowdown = 4
    options.brightness = 75
    options.parallel = 1
    options.hardware_mapping = "adafruit-hat"
    return RGBMatrix(options=options)

matrix = configure_matrix()

# Font loading
def load_fonts():
    fonts = {
        "big": "../../../fonts/10x20.bdf",
        "medium_big": "../../../fonts/7x13B.bdf",
        "medium": "../../../fonts/6x9.bdf",
        "small": "../../../fonts/5x7.bdf"
    }
    return {key: graphics.Font().LoadFont(font_path) for key, font_path in fonts.items()}

fonts = load_fonts()

# Define colors
colors = {
    "mta_g_green": graphics.Color(108, 190, 69),
    "white": graphics.Color(255, 255, 255),
    "half_white": graphics.Color(126, 126, 126),
    "another_white": graphics.Color(50, 50, 50),
    "orange": graphics.Color(194, 89, 29),
    "purple": graphics.Color(78, 0, 130),
    "red": graphics.Color(213, 0, 0),
    "yellow": graphics.Color(201, 181, 0)
}

# Main function to handle transit updates and drawing
def run():
    matrix.Clear()
    transit_times = get_transit()
    if transit_times:
        draw_dividing_lines()
        draw_trains(transit_times.get("train", {}))
        draw_bus(transit_times.get("bus", []))
    else:
        draw_error(95, 16)

# Helper function to fetch transit data
def get_transit():
    try:
        response = requests.get('https://funmirror-server.herokuapp.com/led-sign-transit')
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

# Drawing functions
def draw_error(x, y):
    draw_face(x, y)
    graphics.DrawText(matrix, fonts["big"], 39, 23, colors["half_white"], "ERROR")
    draw_face(110, 16)

def draw_face(x, y):
    graphics.DrawCircle(matrix, x, y, 14, colors["yellow"])
    for offset in [-5, 5]:
        graphics.DrawLine(matrix, x + offset, y - 4, x + offset + 1, y - 4, colors["half_white"])
    graphics.DrawLine(matrix, x - 5, y + 5, x + 5, y + 5, colors["half_white"])

def draw_dividing_lines():
    graphics.DrawLine(matrix, 0, 16, 88, 16, colors["another_white"])
    graphics.DrawLine(matrix, 88, 0, 88, 32, colors["another_white"])

def draw_trains(train_times):
    draw_mta_g()
    draw_station_names()
    if train_times:
        draw_station_times(train_times.get("n", []), draw_court_sq_times)
        draw_station_times(train_times.get("s", []), draw_church_ave_times)
    else:
        draw_no_transit_icon(78, 7)
        draw_no_transit_icon(78, 24)

def draw_station_times(times, draw_function):
    if len(times) >= 2:
        draw_function(times[0], times[1])

def draw_bus(bus_times):
    draw_bus_name()
    if bus_times:
        draw_bus_times(bus_times)
    else:
        draw_no_transit_icon(120, 24)

def draw_mta_g():
    for y in [14, 31]:
        graphics.DrawText(matrix, fonts["big"], 0, y, colors["mta_g_green"], "G")

def draw_station_names():
    graphics.DrawText(matrix, fonts["medium_big"], 13, 12, colors["half_white"], "Court")
    graphics.DrawText(matrix, fonts["medium_big"], 13, 29, colors["half_white"], "Church")

def draw_bus_name():
    graphics.DrawText(matrix, fonts["medium_big"], 107, 10, colors["purple"], "B62")

def draw_bus_times(b62_times):
    y_coords = {1: 24, 2: 17, 3: 10}
    y_coord_base = y_coords.get(len(b62_times), 10)
    for i, mins in enumerate(b62_times, start=1):
        draw_time(mins, 100, y_coord_base + (i * 7))

def draw_time(mins, x, y):
    mins_str = str(mins)
    graphics.DrawText(matrix, fonts["medium"], x + x_coord_time_offset(mins_str), y, colors["white"], mins_str)
    graphics.DrawText(matrix, fonts["small"], x + 13, y, colors["orange"], "min")

def draw_court_sq_times(first_time, second_time):
    draw_times(first_time, second_time, 60, [7, 15])

def draw_church_ave_times(first_time, second_time):
    draw_times(first_time, second_time, 60, [23, 31])

def draw_times(first, second, x, y_coords):
    for time, y in zip([first, second], y_coords):
        draw_time(time, x, y)

def draw_no_transit_icon(x, y):
    graphics.DrawCircle(matrix, x, y, 6, colors["red"])
    graphics.DrawLine(matrix, x - 4, y + 4, x + 4, y - 4, colors["red"])

def x_coord_time_offset(mins):
    return 6 if len(mins) == 1 else 0

# Main loop
if __name__ == "__main__":
    try:
        print("Press CTRL-C to stop.")
        while True:
            run()
            time.sleep(30)
    except KeyboardInterrupt:
        sys.exit(0)
