import dataclasses
from typing import List, Optional
import numpy as np
import cv2


@dataclasses.dataclass
class StitchParams:
    distance_coefficient: float
    min_match_count: int
    ransac_reprojection_threshold: float
    ransac_max_iterations: int
    ransac_confidence: float


@dataclasses.dataclass
class StitchResult:
    M: cv2.typing.MatLike
    world_center_translation_vector: np.ndarray
    world_rotation_angle: np.float32
    world_local_cornerpoints: np.ndarray
    stitched_cornerpoints: np.ndarray
    warped_center_vector: np.ndarray


@dataclasses.dataclass
class LocalizedWireframe:
    data_url: Optional[str]
    world_centerpoint: np.ndarray
    world_rotation: np.float32
    scale: np.float32
    world_corner_points: np.ndarray
    timestamp: np.float32
    frame_number: int
    stitch_result: Optional[StitchResult]


@dataclasses.dataclass
class LocalizedFrame(LocalizedWireframe):
    frame: np.ndarray


@dataclasses.dataclass
class StitchTrail:
    last_localized_frame: LocalizedFrame
    localized_wireframes: list[LocalizedWireframe]


class StitchProcessor:
    '''Stitching implementation'''
    def __init__(self):
        self._trails: List[StitchTrail] = []
        self.last_frame = 0
        self.origin_point = np.array([0., 0.])
        self.origin_rotation = 0.
        self.sift = None
        self.matcher = None
        self.stitch_params = StitchParams(
            distance_coefficient=0.7,
            min_match_count=10,
            ransac_reprojection_threshold=5.0,
            ransac_max_iterations=2000,
            ransac_confidence=0.995
        )
        return super().__init__()

    def apply(self, frame: np.ndarray):
        '''Apply the stitching algorithm'''
        h, w, _ = frame.shape


        extended_trails_count = 0
        for trail in self._trails:
            if is_trail_stale(trail, self.last_frame, 15):
                continue
            stitch_result = self._stitch_two_frames(
                trail.last_localized_frame.frame,
                frame,
                self.stitch_params
            )
            if stitch_result is None:
                continue
            print(stitch_result)
            current_localized_wireframe = self._get_localized_wireframe_from_stitch_result(
                trail.last_localized_frame,
                stitch_result
            )
            current_localized_frame = LocalizedFrame(
                frame = frame,
                **dataclasses.asdict(current_localized_wireframe),
            )
            frame_to_delete = trail.last_localized_frame
            trail.last_localized_frame = current_localized_frame
            del frame_to_delete
            trail.localized_wireframes.append(current_localized_wireframe)
            extended_trails_count += 1

        if extended_trails_count == 0:
            current_localized_wireframe = LocalizedWireframe(
                data_url=None,
                world_centerpoint=self.origin_point,
                world_rotation=0.,
                world_corner_points=np.float32([[-w/2, h/2], [-w/2, -h/2], [w/2, -h/2], [w/2, h/2]]),
                scale=1.,
                timestamp=0.,
                frame_number=self.last_frame,
                stitch_result=None
            )
            current_localized_frame = LocalizedFrame(
                frame = frame,
                **dataclasses.asdict(current_localized_wireframe),
            )
            self._trails.append(StitchTrail(
                last_localized_frame = current_localized_frame,
                localized_wireframes = [current_localized_wireframe]
            ))
        
        self.last_frame += 1

        return self._trails

    def _stitch_two_frames(self, frame1: np.ndarray, frame2: np.ndarray, params: StitchParams):
        '''Stitch two frames'''
        if self.sift is None:
            self.sift = cv2.SIFT_create()
        if self.matcher is None:
            self.matcher = cv2.BFMatcher()

        frame1_gs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        frame2_gs = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        keypoints1, descriptors1 = self.sift.detectAndCompute(frame1_gs, None)
        keypoints2, descriptors2 = self.sift.detectAndCompute(frame2_gs, None)

        matches = self.matcher.knnMatch(descriptors1, descriptors2, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < n.distance * params.distance_coefficient:
                good_matches.append(m)

        if len(good_matches) < params.min_match_count:
            return None
        
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(
            src_pts,
            dst_pts,
            cv2.RANSAC,
            5.0,
            maxIters=params.ransac_max_iterations,
            confidence=params.ransac_confidence
        )

        h, w, _ = frame1.shape
        corner_points = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        stitched_corner_points = cv2.perspectiveTransform(corner_points, M)

        center_vector = np.float32([[w/2, h/2], [w/2, 0]]).reshape(-1, 1, 2)
        warped_center_vector = cv2.perspectiveTransform(center_vector, M)

        # world_center_vector is the end result of the movement in x0y world coordinates
        # where y is up and x is right (i.e. y is inverted relative to image coordinates)
        # world_warped_center_vector is the start of movement in x0y world coordinates
        world_center_vector = image_points_to_world_points(center_vector.reshape(2, 2))
        world_warped_center_vector = image_points_to_world_points(warped_center_vector.reshape(2, 2))

        world_rotation_angle = get_rotation_angle(world_warped_center_vector, world_center_vector)
        world_center_translation_vector = world_center_vector[0] - world_warped_center_vector[0]
        world_local_points = image_points_to_world_points(corner_points.reshape(4, 2))
        centerd_world_local_points = world_local_points + np.float32([-w/2, h/2])
        return StitchResult(
            M=M,
            world_local_cornerpoints=centerd_world_local_points,
            world_rotation_angle=world_rotation_angle,
            world_center_translation_vector=world_center_translation_vector,
            stitched_cornerpoints=stitched_corner_points,
            warped_center_vector=warped_center_vector,
        )

    def _get_localized_wireframe_from_stitch_result(
        self,
        previous_wireframe: LocalizedWireframe,
        stitch_result: StitchResult
    ):
        '''Get a new localized wireframe from a stitch result'''
        rotated_translation = rotate_point_around_origin(
            stitch_result.world_center_translation_vector,
            previous_wireframe.world_rotation
        )
        world_rotation = previous_wireframe.world_rotation + stitch_result.world_rotation_angle
        world_centerpoint = previous_wireframe.world_centerpoint + rotated_translation
        rotated_corner_points = np.array([
            rotate_point_around_origin(point, world_rotation)
            for point in stitch_result.world_local_cornerpoints
        ])
        world_corner_points = rotated_corner_points + world_centerpoint

        return LocalizedWireframe(
            data_url=None,
            world_centerpoint=world_centerpoint,
            world_rotation=world_rotation,
            world_corner_points=world_corner_points,
            scale=previous_wireframe.scale,
            timestamp=previous_wireframe.timestamp, # TODO: Update timestamp
            frame_number=self.last_frame,
            stitch_result=stitch_result
        )


def image_points_to_world_points(points):
    # Mirror the vector around the X-axis
    mirrored_points = np.array([[point[0], -point[1]] for point in points])
    return mirrored_points


def is_trail_stale(trail: StitchTrail, current_frame: int, max_backlog_len: int):
    '''Check if the trail is stale'''
    return current_frame - trail.last_localized_frame.frame_number > max_backlog_len


def angle_between(v1, v2):
    '''Compute the angle between two vectors in radians'''
    # Compute the dot product
    dot_product = np.dot(v1, v2)

    # Compute the magnitudes of the vectors
    v1_magnitude = np.linalg.norm(v1)
    v2_magnitude = np.linalg.norm(v2)

    # Compute the angle in radians
    angle = np.arccos(dot_product / (v1_magnitude * v2_magnitude))

    # Convert the angle to degrees
    angle = np.degrees(angle)

    return angle


def get_rotation_angle(vector1, vector2):
    '''Calculate the angle to rotate vector1 to be parallel to vector2,
    in radians, counterclockwise means positive.'''
    # Calculate the direction of the vectors
    vector1 = vector1.reshape(2, 2)
    vector2 = vector2.reshape(2, 2)
    direction1 = vector1[1] - vector1[0]
    direction2 = vector2[1] - vector2[0]

    # Calculate the angles with the x-axis
    angle1 = np.arctan2(direction1[1], direction1[0])
    angle2 = np.arctan2(direction2[1], direction2[0])

    # Calculate the rotation angle
    rotation_angle = angle2 - angle1

    return rotation_angle


def rotate_point_around_origin(point, angle):
    '''Rotate a point around the origin, given angle in radians'''
    # Define the rotation matrix
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle),  np.cos(angle)]])

    # Rotate the point
    rotated_point = np.dot(rotation_matrix, point)

    return rotated_point
