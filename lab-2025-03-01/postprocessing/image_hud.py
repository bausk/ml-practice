import cv2
import numpy as np

class ImageHUD:
    def __init__(self) -> None:
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.4
        self.lower_font_scale = 0.30
        self.colors = [
            (255, 255, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
            (0, 0, 0),
        ]
        self.yoffset = 20
        self.thickness = 1
        self.boxwidth = 100
        cv2.namedWindow('preview')

    def setImage(self, frame: cv2.typing.MatLike):
        self.frame = frame

    def render(self):
        cv2.imshow('preview', self.frame)

    def destroy(self):
        cv2.destroyWindow('preview')

    @property
    def centerpoint(self):
        return (self.frame.shape[1] // 2, self.frame.shape[0] // 2)

    def write_uppertext(self, text: str, position: int):
        hud_magnification = self.frame.shape[1] / 700
        y_offset = int(self.yoffset * hud_magnification)
        x_offset = int((10 * position + self.boxwidth * (position - 1)) * hud_magnification)
        cv2.putText(
            self.frame,
            text,
            (x_offset, y_offset),
            self.font,
            self.font_scale * hud_magnification,
            self.colors[position - 1],
            int(self.thickness * hud_magnification),
            lineType=cv2.LINE_AA,
        )
        return self.frame

    def write_lowertext(self, text: str, position: int):
        hud_magnification = self.frame.shape[1] / 700
        y_offset = int(self.frame.shape[0] - int(self.yoffset * 3) * hud_magnification)
        x_offset = int(10 * position + self.boxwidth * (position - 1) * hud_magnification)
        strings = text.split('\n')
        for i, line in enumerate(strings):
            cv2.putText(
                self.frame,
                line,
                (x_offset, y_offset + int(9 * i * hud_magnification)),
                self.font,
                self.lower_font_scale * hud_magnification,
                self.colors[position - 1],
                int(self.thickness * hud_magnification),
                lineType=cv2.LINE_AA,
            )
        return self.frame

    def draw_central_vector(self, vector: tuple, position: int):
        vis_vector = vector.astype(int)
        if not np.any(vis_vector):
            return self.frame

        x_center = self.frame.shape[1] // 2
        y_center = self.frame.shape[0] // 2
        x_end = x_center + vis_vector[0]
        y_end = y_center + vis_vector[1]
        cv2.arrowedLine(self.frame, (x_center, y_center), (x_end, y_end), self.colors[position - 1], 2)
        return self.frame
