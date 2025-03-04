from typing import Optional
import cv2

from preprocessing.image_operations import crop_cv_image_centered, resize_cv_image_to_maxwidth


class BaseVideoInput:
    def __init__(self) -> None:
        self.crop_factor = None
        self.resize_maxwidth = None
        self.is_finished = False

    def _initialize_preprocess_frame(self, crop_factor: float = 1, resize_maxwidth: Optional[int] = None) -> None:
        self.crop_factor = crop_factor
        self.resize_maxwidth = resize_maxwidth

    def capture(self) -> cv2.typing.MatLike:
        raise NotImplementedError('implement capture function')

    def preprocess_frame(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        cropped = frame if self.crop_factor is None else crop_cv_image_centered(frame, self.crop_factor)
        resized = frame if self.resize_maxwidth is None else resize_cv_image_to_maxwidth(cropped, max_width=self.resize_maxwidth)
        return resized

    def destroy(self):
        pass
