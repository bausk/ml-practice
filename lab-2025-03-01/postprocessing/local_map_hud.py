from typing import List
import cv2
import numpy as np

from processing.stitch_processor import LocalizedWireframe, StitchTrail


class LocalMapHUD:
    def __init__(self) -> None:
        self.colors = [
            (0, 255, 0),
            (255, 0, 0),
            (0, 0, 255),
            (255, 255, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
            (0, 0, 0),
        ]
        self.image_width = 500
        self.image_height = 500
        cv2.namedWindow('Local Map')

    def render(self, trails: List[StitchTrail]):
        offset_x, offset_y, width, height = self.find_max_dimensions(trails)
        side = max(width, height)
        image = np.zeros((side, side, 3), np.uint8)
        resize_factor = width / self.image_width
        thickness = 20 if resize_factor > 6 else 10 if resize_factor > 3 else 3
        for i, trail in enumerate(trails):
            for wireframe in trail.localized_wireframes:
                polyline = world_points_to_image(wireframe.world_corner_points, offset_x, offset_y, height)
                image = cv2.polylines(image, [np.int32(polyline)], True, self.colors[i], thickness, cv2.LINE_AA)

        image = cv2.resize(image, (self.image_width, self.image_height))
        cv2.imshow('Local Map', image)

    def find_max_dimensions(self, trails: List[StitchTrail]):
        max_x = 1
        min_x = -1
        max_y = 1
        min_y = -1
        for trail in trails:
            for wireframe in trail.localized_wireframes:
                for point in wireframe.world_corner_points:
                    max_x = max(max_x, point[0])
                    min_x = min(min_x, point[0])
                    max_y = max(max_y, point[1])
                    min_y = min(min_y, point[1])
        return (min_x, min_y, int(max_x - min_x), int(max_y - min_y))

    def predraw_wireframe(self, wireframe: LocalizedWireframe, image_dimensions: List[int]):
        polyline = wireframe.world_corner_points
        image_dimensions[0] = max(image_dimensions[0], int(np.max(polyline[:, 0])))
        image_dimensions[1] = max(image_dimensions[1], int(np.max(polyline[:, 1])))
        return image_dimensions, polyline
    

def world_points_to_image(points: np.ndarray, offset_x: int, offset_y: int, height: int):
    return np.array([
        [
            int(point[0] - offset_x),
            int(height - (point[1] - offset_y)),
        ]
        for point in points
    ])
