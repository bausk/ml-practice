import numpy as np

def get_principals_from_transformation_matrix(affine_transformation_matrix):
    # Extract the rotation angle (in radians)
    theta = np.arctan2(affine_transformation_matrix[1, 0], affine_transformation_matrix[0, 0])

    # Convert the rotation angle to degrees
    theta = np.degrees(theta)

    # Extract the translation vector
    translation_vector = affine_transformation_matrix[:, 2]

    return theta, translation_vector
