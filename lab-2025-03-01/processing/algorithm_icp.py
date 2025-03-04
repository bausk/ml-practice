import numpy as np
from sklearn.neighbors import NearestNeighbors


def icp(
        source_points: np.ndarray,
        target_points: np.ndarray,
        initial_pose: np.ndarray = None,
        max_iterations=20,
        tolerance=1
    ):
    """
    Finds the best fit between two sets of points using the Iterative Closest Point (ICP) algorithm.

    Args:
        source_points (numpy.ndarray): Array of source points.
        target_points (numpy.ndarray): Array of target points.
        max_iterations (int): Maximum number of iterations.
        tolerance (float): Tolerance for convergence.

    Returns:
        numpy.ndarray: Transformed source points that best align with the target points.
    """
    assert source_points.shape == target_points.shape

    # Get number of dimensions
    m = source_points.shape[1]

    # make points homogeneous, copy them to maintain the originals
    src = np.ones((m + 1, source_points.shape[0]))
    dst = np.ones((m + 1, target_points.shape[0]))
    src[:m, :] = np.copy(source_points.T)
    dst[:m, :] = np.copy(target_points.T)

    # apply the initial pose estimation
    if initial_pose is not None:
        src = np.dot(initial_pose, src)

    prev_error = 0

    for i in range(max_iterations):
        # find the nearest neighbors between the current source and destination points
        distances, indices = nearest_neighbor(src[:m, :].T, dst[:m, :].T)

        # compute the transformation between the current source and nearest destination points
        T, _, _ = best_fit_transform(src[:m, :].T, dst[:m, indices].T)

        # update the current source
        src = np.dot(T, src)

        # check error
        mean_error = np.mean(distances)
        if np.abs(prev_error - mean_error) < tolerance:
            break
        prev_error = mean_error

    # calculate final transformation
    T, rotM, trVector = best_fit_transform(source_points, src[:m,:].T)
    theta_rad = np.arctan2(rotM[1, 0], rotM[0, 0])
    return T, theta_rad, trVector, distances, i


    # transformed_points = source_points.copy()

    # for iteration in range(max_iterations):
    #     # Find the nearest neighbors between the source and target points
    #     tree = KDTree(target_points)
    #     distances, indices = tree.query(transformed_points)

    #     # Compute the transformation matrix using the least squares method
    #     A = np.hstack((source_points[indices], np.ones((len(indices), 1))))
    #     b = transformed_points - target_points[indices]
    #     transformation_matrix, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    #     # Apply the transformation to the source points
    #     transformed_points = np.dot(source_points, transformation_matrix[:-1]) + transformation_matrix[-1]

    #     # Check for convergence
    #     if np.sum(distances) < tolerance:
    #         break

    # return transformed_points


def nearest_neighbor(src: np.ndarray, dst: np.ndarray):
    '''
    Find the nearest (Euclidean) neighbor in dst for each point in src
    Input:
        src: Nxm array of points
        dst: Nxm array of points
    Output:
        distances: Euclidean distances of the nearest neighbor
        indices: dst indices of the nearest neighbor
    '''

    assert src.shape == dst.shape

    neigh = NearestNeighbors(n_neighbors=1)
    neigh.fit(dst)
    distances, indices = neigh.kneighbors(src, return_distance=True)
    return distances.ravel(), indices.ravel()


def best_fit_transform(A: np.ndarray, B: np.ndarray):
    '''
    Calculates the least-squares best-fit transform that maps corresponding points A to B in m spatial dimensions
    Input:
      A: Nxm numpy array of corresponding points
      B: Nxm numpy array of corresponding points
    Returns:
      T: (m + 1)x(m + 1) homogeneous transformation matrix that maps A on to B
      R: mxm rotation matrix
      t: mx1 translation vector
    '''

    assert A.shape == B.shape

    # get number of dimensions
    m = A.shape[1]

    # translate points to their centroids
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # special reflection case
    if np.linalg.det(R) < 0:
       Vt[m - 1, :] *= -1
       R = np.dot(Vt.T, U.T)

    # translation
    t = centroid_B.T - np.dot(R, centroid_A.T)

    # homogenous transformation
    T = np.identity(m + 1)
    T[:m, :m] = R
    T[:m, m] = t

    return T, R, t
