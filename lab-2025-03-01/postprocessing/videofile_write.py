from operator import is_
import time
import cv2
import os


class MP4VideoWriter:
    def __init__(self, task_name: str, video_fps = 60) -> None:
        self.task_name = task_name
        self.video_out = None
        self.video_fps = video_fps
        self.capture_folder = None
        self.video_file_name = None

    def write_frame(self, frame: cv2.typing.MatLike):
        if self.video_out is None:
            cwd = os.getcwd()
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
            self.video_file_name = f'{self.task_name}_{video_width_px}x{video_height_px}_{time.strftime("%Y%m%d-%H%M%S")}'
            self.video_out = cv2.VideoWriter(
                f'{self.video_file_name}.mp4',
                cv2.VideoWriter.fourcc(*'mp4v'),
                self.video_fps,
                (video_width_px, video_height_px)
            )
            os.chdir(cwd)

        self.video_out.write(frame)

    def capture_screen_frame(self, frame: cv2.typing.MatLike):
        video_width_px = frame.shape[1]
        video_height_px = frame.shape[0]

        cwd = os.getcwd()
        if self.capture_folder is None:
            path = f'outputs'
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
            capture_folder_name = (
                self.video_file_name if self.video_file_name is not None
                else f'{self.task_name}_{video_width_px}x{video_height_px}_{time.strftime("%Y%m%d-%H%M%S")}'
            )
            try:
                os.mkdir(capture_folder_name)
            except FileExistsError:
                pass
            os.chdir(capture_folder_name)
            self.capture_folder = os.getcwd()
        else:
            os.chdir(self.capture_folder)
        capture_file_name = f'{self.task_name}_{video_width_px}x{video_height_px}_{time.strftime("%Y%m%d-%H%M%S")}.png'
        cv2.imwrite(capture_file_name, frame)
        os.chdir(cwd)

    def cleanup(self):
        self.video_out.release()
