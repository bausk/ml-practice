import cv2
import numpy as np


class Camera:
    def __init__(self, sensor_width_mm, hfov_deg, image_width_pixels, image_height_pixels=None, p_point=None, fisheye=False, distortion_coefficients=None):
        if distortion_coefficients is None:
            distortion_coefficients = np.array([0.0, 0.0, 0.0, 0.0])
        self.distortion_coefficients = distortion_coefficients
        self.focal_distance = self._calculate_focal_distance(sensor_width_mm, hfov_deg, image_width_pixels)

        self.image_width_pixels = image_width_pixels
        self.image_height_pixels = image_height_pixels
        if p_point is None:
            self.p_point = (image_width_pixels / 2, image_width_pixels / 2)
        else:
            self.p_point = (0.0, 0.0)
        self.hfov_deg = hfov_deg
        self.fisheye = fisheye

    def _calculate_focal_distance(self, sensor_width_mm, hfov_deg, image_width_pixels):
        focal_length_mm = sensor_width_mm / 2 / np.tan(np.radians(hfov_deg / 2))
        return focal_length_mm * (image_width_pixels / sensor_width_mm)

    @property
    def camera_matrix(self):
        return self.get_camera_matrix()

    def get_camera_matrix(self):
        return np.array([[self.focal_distance, 0, self.p_point[0]],
                         [0, self.focal_distance, self.p_point[1]],
                         [0, 0, 1]])

    def get_undistorted_points(self, points):
        camera_matrix = self.get_camera_matrix()
        points_homogeneous = cv2.convertPointsToHomogeneous(points)
        points_homogeneous_reshaped = np.reshape(points_homogeneous, (-1, 3))
        points_projected_reshaped = np.dot(camera_matrix, points_homogeneous_reshaped.T)
        points_projected = np.reshape(points_projected_reshaped.T, (-1, 1, 3))
        points_cartesian = cv2.convertPointsFromHomogeneous(points_projected)
        return cv2.fisheye.undistortPoints(points_cartesian, camera_matrix, self.distortion_coefficients)
        # return cv2.undistortPoints(points, camera_matrix, self.distortion_coefficients)