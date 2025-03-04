from typing import Annotated, Literal, TypeVar
import numpy as np
import numpy.typing as npt


DType = TypeVar('DType', bound=np.generic)
NPPoint2D = Annotated[npt.NDArray[DType], Literal[2]]
ArrayNxMx2 = Annotated[npt.NDArray[DType], Literal['N', 'M', 2]]


def get_sparse_planes_from_dense_optical_flow(
    motion_vector_field: ArrayNxMx2[np.float32],
    D: float,
    percentile: int = 80
):
    """
    Given a dense optical flow motion vector field, return the "from" and "to" matrices for aggregation inference.
    :param motion_vector_field: The motion vector field.
    :param D: The distance between points in the grid.
    :param origin: The origin of the grid.
    :param percentile: The percentile of the motion vector lengths to use as a threshold, by default 80.
    :return: The "from" and "to" matrices.
    """

    centerpoint = np.array([motion_vector_field.shape[1] // 2, motion_vector_field.shape[0] // 2])

    # Create a grid of points for the "from" matrix
    X, Y = np.meshgrid(
        (np.arange(0, motion_vector_field.shape[1]) - centerpoint[0]) * D,
        (np.arange(0, motion_vector_field.shape[0]) - centerpoint[1]) * D,
    )
    from_matrix = np.dstack([X, Y])

    # Create the "to" matrix by adding the motion vectors to the "from" matrix
    to_matrix = from_matrix + motion_vector_field

    # Calculate the length of each motion vector
    lengths = np.sqrt(np.sum(motion_vector_field**2, axis=2))

    # Find the percentile of the lengths
    percentile = np.percentile(lengths, percentile)

    # Create a mask that selects only the vectors with a length greater than the 90th percentile
    mask = lengths > percentile

    # Apply the mask to the "from" and "to" matrices
    from_matrix_filtered = from_matrix[mask]
    to_matrix_filtered = to_matrix[mask]

    return from_matrix_filtered, to_matrix_filtered
