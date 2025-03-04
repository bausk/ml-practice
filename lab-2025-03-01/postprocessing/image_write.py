import time
import cv2
import os


class ScreencaptureWriter:
    def __init__(self, task_name: str) -> None:
        self.task_name = task_name
        self.video_out = None

    def write_image(self, frame: cv2.typing.MatLike):
        if self.video_out is None:
            path = f'outputs'
            video_width_px = frame.shape[1]
            video_height_px = frame.shape[0]
            folder = f'{self.task_name}_{video_width_px}x{video_height_px}'

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
            vide_file_name = f'{self.task_name}_{video_width_px}x{video_height_px}_{time.strftime("%Y%m%d-%H%M%S")}.mp4'
            self.video_out = cv2.VideoWriter(
                vide_file_name,
                cv2.VideoWriter.fourcc(*'mp4v'),
                self.video_fps,
                (video_width_px, video_height_px)
            )

        self.video_out.write(frame)

    def cleanup(self):
        self.video_out.release()
