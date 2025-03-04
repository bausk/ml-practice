import cv2
import numpy as np

from processing.camera import Camera
from processing.motion_calculation import estimate_sparse_principals_icp, infer_dense_rotation_translation, estimate_sparse_principals_affine2D
from processing.optical_flow import SparseResult
from processing.base_tracking import BaseInference, BaseSparseInference


default_camera = Camera(
    sensor_width_mm=1/2.3 * 25.4,
    hfov_deg=150,
    image_width_pixels=900,
    distortion_coefficients=np.array([-0.0001, -0.0001, 0.0, 0.0])
)


class CompoundVectorInferenceDense(BaseInference):
    def __init__(self, percentile) -> None:
        self.rotation_angles = []
        self.translation_vectors = []
        self.cumulative_motion_vector = np.array([0.0, 0.0])
        self.percentile: int = percentile

    def infer(self, vector_field: cv2.typing.MatLike):
        rotation_angle, translation_vector = infer_dense_rotation_translation(vector_field, self.percentile)
        self.rotation_angles.append(rotation_angle)
        self.translation_vectors.append(translation_vector)
        rotation_angle_rad = -np.radians(rotation_angle)
        rotation_matrix = np.array([[np.cos(rotation_angle_rad), -np.sin(rotation_angle_rad)],
                                     [np.sin(rotation_angle_rad), np.cos(rotation_angle_rad)]])
        self.cumulative_motion_vector = np.dot(rotation_matrix, self.cumulative_motion_vector)
        self.cumulative_motion_vector += translation_vector
        return self.cumulative_motion_vector
    
    def get_title_message(self):
        return f'{self.percentile}%'
    
    def get_parameter_message(self):
        return f'{self.percentile}%'


class CompoundVectorInferenceSparse(BaseSparseInference):
    def __init__(self, initial_motion_vector=None, estimator_algo=None, camera=None, undistort=False) -> None:
        self.rotation_angles = []
        self.translation_vectors = []
        if initial_motion_vector is None:
            initial_motion_vector = np.array([0.0, 0.0])
        self.initial_motion_vector = initial_motion_vector
        self.cumulative_motion_vector = np.array([0.0, 0.0])
        # Camera parameters
        if camera is None:
            camera = default_camera
        self.camera = camera
        self.undistort = undistort
        if estimator_algo is None:
            self.estimator_algo = 'AFFINE'
        else:
            self.estimator_algo = estimator_algo

    def infer(self, result: SparseResult):
        from_field, to_field = result.old_points, result.new_points

        if self.undistort:
            from_points_cartesian = self.camera.get_undistorted_points(from_field)
            to_points_cartesian = self.camera.get_undistorted_points(to_field)
        else:
            from_points_cartesian = from_field
            to_points_cartesian = to_field

        if self.estimator_algo == 'ICP':
            rotation_angle, translation_vector = estimate_sparse_principals_icp(from_points_cartesian, to_points_cartesian)
        else:
            rotation_angle, translation_vector = estimate_sparse_principals_affine2D(from_points_cartesian, to_points_cartesian)

        # rotation_angle, translation_vector = infer_sparse_rotation_translation(from_field, to_field)
        self.rotation_angles.append(rotation_angle)
        self.translation_vectors.append(translation_vector)
        rotation_angle_rad = np.radians(rotation_angle)
        rotation_matrix = np.array([[np.cos(rotation_angle_rad), -np.sin(rotation_angle_rad)],
                                     [np.sin(rotation_angle_rad), np.cos(rotation_angle_rad)]])
        self.cumulative_motion_vector: np.ndarray = np.dot(rotation_matrix, self.cumulative_motion_vector)
        self.initial_motion_vector: np.ndarray = np.dot(rotation_matrix, self.initial_motion_vector)
        self.cumulative_motion_vector += translation_vector
        return [self.cumulative_motion_vector, self.initial_motion_vector]
    
    def get_title_message(self):
        return f'CMPND {self.estimator_algo}'
    
    def get_parameter_message(self):
        return f'''UNDSTRT: {'Y' if self.undistort else 'N'}
        \nCAM: f{self.camera.focal_distance:.2f}
        \n{self.cumulative_motion_vector[0]:.2f}, {self.cumulative_motion_vector[1]:.2f}
        '''


class StaticVectorInferenceSparse(BaseSparseInference):
    def __init__(self, initial_motion_vector=None, estimator_algo=None, camera=None, undistort=False) -> None:
        self.starting_field: cv2.typing.MatLike = None

        if camera is None:
            camera = default_camera
        self.camera = camera

        if initial_motion_vector is None:
            initial_motion_vector = np.array([0.0, 0.0])
        self.initial_motion_vector = initial_motion_vector
        self.motion_vector = np.array([0.0, 0.0])
        self.undistort = undistort
        self.current_translation_vector = None
        if estimator_algo is None:
            self.estimator_algo = 'AFFINE'
        else:
            self.estimator_algo = estimator_algo


    def infer(self, result: SparseResult):
        """
        Static Spare Inference infers translation vector from the first frame to the current frame.
        To get point pairs, first frame needs to be filtered by the new valid positions filter.
        """
        to_field, valid_positions = result.new_pixels, result.valid_positions
        if self.starting_field is None:
            self.starting_field = result.original_points
            from_field = self.starting_field
        else:
            from_field = self.starting_field.reshape(-1, 1, 2)[valid_positions==1]
        
        if self.undistort:
            from_points_cartesian = self.camera.get_undistorted_points(from_field)
            to_points_cartesian = self.camera.get_undistorted_points(to_field)
        else:
            from_points_cartesian = from_field
            to_points_cartesian = to_field

        if self.estimator_algo == 'ICP':
            theta, translation_vector = estimate_sparse_principals_icp(from_points_cartesian, to_points_cartesian)
        else:
            theta, translation_vector = estimate_sparse_principals_affine2D(from_points_cartesian, to_points_cartesian)
        self.starting_field = from_field
        self.current_translation_vector = translation_vector

        theta_radians = np.radians(theta)
        R = np.array([[np.cos(theta_radians), -np.sin(theta_radians)],
              [np.sin(theta_radians),  np.cos(theta_radians)]])
        self.initial_motion_vector: np.ndarray = np.dot(R, self.initial_motion_vector)
        self.motion_vector = translation_vector
        return [self.motion_vector, self.initial_motion_vector]

    def get_title_message(self):
        return f'STATIC {self.estimator_algo}'

    def get_parameter_message(self):
        return f'''UNDSTRT: {'Y' if self.undistort else 'N'}
        \nCAM: f{self.camera.focal_distance:.2f}
        \n{self.current_translation_vector[0]:.2f}, {self.current_translation_vector[1]:.2f}
        '''
