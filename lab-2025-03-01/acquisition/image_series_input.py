import glob
import time
from typing import Optional
import cv2

from acquisition.base_video_input import BaseVideoInput


class SavedImageSeriesInput(BaseVideoInput):
    def __init__(self, path: str, crop_factor: Optional[float] = 1, resize_maxwidth: Optional[int] = None) -> None:
        super().__init__()
        self._path = path
        self._next_frame = None
        self._filenames = []
        self.last_timestamp = None
        self.is_finished = False
        self._initialize_preprocess_frame(crop_factor, resize_maxwidth)

    def capture(self):
        if self._next_frame is None:
            self._filenames = sorted(glob.glob(f'{self._path}/*'))
            self._next_frame = 0
        
        new_timestamp = time.time()
        message = ''
        if self.last_timestamp is None:
            self.last_timestamp = new_timestamp
            difference_seconds = 0.001
        else:
            difference_seconds = new_timestamp - self.last_timestamp
            message += f'Overall FPS: {(1/difference_seconds):02f}. '
            self.last_timestamp = new_timestamp

        while True:
            if self._next_frame >= len(self._filenames):
                self.is_finished = True
                return None

            filename_to_read = self._filenames[self._next_frame]

            try:
                result = cv2.imread(filename_to_read)
                result = self.preprocess_frame(result)
                self._next_frame += 1
                timestamp_after_extraction = time.time()
                algo_difference_seconds = difference_seconds - (timestamp_after_extraction - new_timestamp)
                message += f'Algorithm part is: {(algo_difference_seconds / difference_seconds * 100):02f}. '
                print(message, end='\r')
                return result
            except Exception:
                self._next_frame += 1

    def destroy(self):
        return super().destroy()
