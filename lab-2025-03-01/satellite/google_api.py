import os
import cv2
import numpy as np
import requests
from io import BytesIO

API_KEY = os.getenv('GOOGLE_API_KEY')

LEVEL_TO_ZOOM_MAP = {
    0: 19,
    1: 18,
    2: 17,
    3: 16,
    4: 14,
    5: 12,
}


def crop_copyright(image: np.ndarray):
    start_row, start_col = int(20), int(20)
    end_row, end_col = int(image.shape[0] - 20), int(image.shape[1] - 20)
    cropped = image[start_row:end_row , start_col:end_col]
    return cropped


def get_static_map(latitude: str, longitude: str, level: int, size='640x640', maptype='satellite'):
    zoom = LEVEL_TO_ZOOM_MAP[level]
    url = f'https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom={zoom}&size={size}&maptype={maptype}&key={API_KEY}'
    response = requests.get(url)
    stream = BytesIO(response.content)
    bytes_arr = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(bytes_arr, cv2.IMREAD_COLOR)
    return crop_copyright(image)
