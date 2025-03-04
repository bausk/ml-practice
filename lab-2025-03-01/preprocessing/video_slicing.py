import time
from typing import Optional
import click
import cv2
import math
import os

from preprocessing.image_operations import crop_cv_image_centered, resize_cv_image_to_maxwidth


class MP4VideoSlicer:
    def __init__(self, video_path, autoincrement=True, increment=None, crop_factor=None, resize_maxwidth=None) -> None:
        capture_source = cv2.VideoCapture(video_path)
        if crop_factor is None:
            crop_factor = 1.0
        self.crop_factor = crop_factor
        self.resize_maxwidth = resize_maxwidth
        self.video_fps: float = capture_source.get(cv2.CAP_PROP_FPS)
        self.total_frames: int = int(capture_source.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture_source.get(3))
        height = int(capture_source.get(4))

        is_should_resize = resize_maxwidth is not None and width > resize_maxwidth
        self.should_preprocess = True if is_should_resize or crop_factor != 1 else False

        if is_should_resize:
            scale_factor = resize_maxwidth / width
            resized_height = int(height * scale_factor)
            self.video_width_px = resize_maxwidth
            self.video_height_px = resized_height
        else:
            self.video_width_px = width
            self.video_height_px = height

        self.capture_source = capture_source
        self.next_step_seconds = 0.0
        self.frame_count = 0
        self.autoincrement = autoincrement
        self.increment = increment

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.autoincrement:
            if self.increment is None:
                next_frame_count = self.frame_count + 1
            else:
                next_frame_count = self.frame_count + math.ceil(self.increment * self.video_fps)
        else:
            next_frame_count = self.frame_count + math.ceil(self.next_step_seconds * self.video_fps)

        if next_frame_count >= self.total_frames:
            self.cleanup()
            raise StopIteration

        if self.autoincrement and self.increment is None:
            # Reading frame one by one does not require setting CAP_PROP_POS_FRAMES
            ret, frame = self.capture_source.read()
        else:
            self.capture_source.set(cv2.CAP_PROP_POS_FRAMES, next_frame_count)
            ret, frame = self.capture_source.read()

        if self.should_preprocess:
            frame = resize_cv_image_to_maxwidth(crop_cv_image_centered(frame, self.crop_factor), max_width=self.video_width_px)
        self.frame_count = next_frame_count
        return ret, frame
    
    def cleanup(self):
        self.capture_source.release()


# TODO: Replace the logic with MP4VideoWriter, refactor into glue class using MP4VideoSlicer directly
# and MP4VideoWriter.
class MP4VideoPreprocessor(MP4VideoSlicer):
    def __init__(
        self,
        video_path,
        autoincrement=True,
        increment=None,
        crop_factor=None,
        resize_maxwidth=None,
    ) -> None:
        super().__init__(video_path, autoincrement, increment, crop_factor, resize_maxwidth)
        base_name = os.path.basename(video_path)
        file_name_without_extension = os.path.splitext(base_name)[0]
        self.task_name = file_name_without_extension
        self.video_out = None


    def process(self, output_format: Optional[str]):
        if output_format is not None:
            path = f'outputs'
            folder = f'{self.task_name}_{self.video_width_px}x{self.video_height_px}'

            try:
                os.mkdir(path)
            except FileExistsError:
                pass
            os.chdir(path)
            try:
                os.mkdir(folder)
            except FileExistsError:
                pass
            os.chdir(folder)        

            if output_format in ['VIDEO', 'ALL']:
                vide_file_name = f'{self.task_name}_{self.video_width_px}x{self.video_height_px}_{time.strftime("%Y%m%d-%H%M%S")}.mp4'
                self.video_out = cv2.VideoWriter(
                    vide_file_name,
                    cv2.VideoWriter.fourcc(*'mp4v'),
                    self.video_fps,
                    (self.video_width_px, self.video_height_px)
                )

        for ret, frame in self:
            if ret:
                if output_format in ['VIDEO', 'ALL']:
                    self.video_out.write(frame)
                if output_format in ['JPG', 'ALL']:
                    current_frame_time_seconds = self.frame_count / self.video_fps
                    hours = int(current_frame_time_seconds // 3600)
                    minutes = int((current_frame_time_seconds % 3600) // 60)
                    seconds = int(current_frame_time_seconds % 60)
                    milliseconds = int((current_frame_time_seconds - int(current_frame_time_seconds)) * 1000)
                    filename = f'output_{self.video_width_px}x{self.video_height_px}_{hours:02d}_{minutes:02d}_{seconds:02d}_{milliseconds:03d}.jpg'
                    cv2.imwrite(filename, frame)
        self.video_out.release()
