import cv2


class StitchHUD:
    def __init__(self) -> None:
        cv2.namedWindow('stitched')

    def render(self, image):
        cv2.imshow('stitched', image)

