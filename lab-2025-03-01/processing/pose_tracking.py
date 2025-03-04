import cv2
import numpy as np

from processing.camera import Camera
from processing.optical_flow import SparseResult
from processing.base_tracking import BaseInference


class CompoundPoseInference(BaseInference):
    def __init__(self, percentile, camera=None) -> None:
        self.rotation_angles = []
        self.translation_vectors = []
        self.cumulative_motion_vector = np.array([0.0, 0.0])
        self.percentile: int = percentile
        # Camera parameters
        if camera is None:
            camera = Camera(sensor_width_mm=1/2.3 * 25.4, hfov_deg=140, image_width_pixels=900)
        self.camera = camera
    
        print(f'Focal distance: {self.camera.focal_distance:.2f} pixels')
        self.ransac_probability = 0.999
        self.ransac_threshold = 1.0
        # Initialize total pose
        self.total_R = np.array([[ 1.,  0.,  0.],
                                 [ 0.,  1.,  0.],
                                 [ 0.,  0.,  1.]])
        self.total_r = np.array([[ 1.,  0.,  0.],
                                 [ 0.,  1.,  0.],
                                 [ 0.,  0.,  1.]])
        self.total_t = np.zeros((3, 1))

    def _calculate_current_threshold(self, from_vector, to_vector):
        # Calculate the distances between corresponding points
        distances = np.sqrt(np.sum((from_vector - to_vector)**2, axis=1))
        self.ransac_threshold = np.percentile(distances, self.percentile)
        if self.ransac_threshold < 0.001:
            self.ransac_threshold = 1

    def infer(self, result: SparseResult):
        from_field, to_field = result.old_points, result.new_points

        # Update threshold (stateful to be able to independently print parameter message)
        self._calculate_current_threshold(from_field, to_field)

        # Recover pose
        camera_matrix = self.camera.get_camera_matrix()

        # Calculate essential matrix
        E, mask = cv2.findEssentialMat(
            from_field,
            to_field,
            cameraMatrix=camera_matrix,
            method=cv2.RANSAC,
            prob=self.ransac_probability,
            threshold=self.ransac_threshold
        )


        _, R, t, mask2 = cv2.recoverPose(E, from_field, to_field, camera_matrix, mask)

        r = np.array([[ R[0][0],  R[0][1],  0.],
                      [ R[0][1],  -R[0][0],  0.],
                      [ 0.,  0.,  1.]])
        
        # Update total pose
        self.total_R = r.dot(self.total_R)
        self.total_t = r.dot(self.total_t) + t
        self.total_r = r
        # self.rotation_angles.append(self.total_R)
        # self.translation_vectors.append(self.total_t)
        self.cumulative_motion_vector = self.total_t[:2, 0]
        return self.cumulative_motion_vector

    def get_title_message(self):
        return f'POSE {self.percentile}%'

    def get_parameter_message(self):
        np.set_printoptions(precision=4)
        return f'''F {self.camera.focal_distance:.1f} THRESH {self.ransac_threshold:.2f}
                 \nR {self.total_r[0]}   T {self.total_t[0]}
                 \nR {self.total_r[1]}   T {self.total_t[1]}
                 \nR {self.total_r[2]}   T {self.total_t[2]}
        '''
