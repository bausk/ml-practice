import cv2
import numpy as np

from preprocessing.plane import get_sparse_planes_from_dense_optical_flow
from processing.algorithm_icp import icp
from processing.matrix_operations import get_principals_from_transformation_matrix


def infer_dense_rotation_translation(optical_flow_motion_field: np.ndarray, percentile=80):
    from_field, to_field = get_sparse_planes_from_dense_optical_flow(
            optical_flow_motion_field,
            1.0,
            percentile
        )
    affine_transformation_matrix, inliers = cv2.estimateAffinePartial2D(
        from_field,
        to_field
    )

    theta, translation_vector = get_principals_from_transformation_matrix(affine_transformation_matrix)
    return theta, translation_vector


def estimate_sparse_principals_affine2D(from_field: np.ndarray, to_field: np.ndarray):
    if len(from_field.shape) > len(to_field.shape):
        from_field = from_field.reshape(-1, 2)

    affine_transformation_matrix, inliers = cv2.estimateAffinePartial2D(
        from_field,
        to_field
    )

    theta, translation_vector = get_principals_from_transformation_matrix(affine_transformation_matrix)
    return theta, translation_vector


def estimate_sparse_principals_icp(from_field: np.ndarray, to_field: np.ndarray):
    # Use the ICP algorithm to estimate the affine transformation matrix
    if len(from_field.shape) > len(to_field.shape):
        from_field = from_field.reshape(-1, 2)

    _, theta_rad, translation_vector, _, _ = icp(
        from_field,
        to_field,
        initial_pose=None,
    )

    return np.degrees(theta_rad), translation_vector
