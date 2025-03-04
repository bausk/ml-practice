
import math
import re


LEVEL3_X_STEP_DEGREES = 0.007
LEVEL3_Y_STEP_DEGREES = 0.005


def lat_degrees_to_meters(lat_degrees):
    return lat_degrees * 111_111


def lon_degrees_to_meters(lon_degrees, lat_degrees):
    return lon_degrees * 111_111 * math.cos(math.radians(lat_degrees))


def dms_to_decimal(position: str):
    degrees, minutes, seconds, direction = re.match(r"(\d+)°(\d+)'([\d.]+)\"([NSWE])", position).groups()
    degrees = int(degrees)
    minutes = int(minutes)
    seconds = float(seconds)
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['S','W']:
        decimal *= -1
    return decimal
