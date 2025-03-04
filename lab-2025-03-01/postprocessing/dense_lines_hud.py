import cv2
import numpy as np

from postprocessing.image_hud import ImageHUD


class DenseLinesHUD:
    def __init__(self, step=32):
        self.step = step

    def draw(self, visualizer: ImageHUD, inference_result):
        h, w = visualizer.frame.shape[:2]
        y, x = np.mgrid[self.step//2:h:self.step, self.step//2:w:self.step].reshape(2,-1)
        fx, fy = inference_result[y,x].T
        lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
        lines = np.int32(lines + 0.5)
        # visualized_image = cv2.cvtColor(visualizer.frame, cv2.COLOR_GRAY2BGR)
        visualized_image = visualizer.frame
        cv2.polylines(visualized_image, lines, 0, (0, 255, 0))
        for (x1, y1), (x2, y2) in lines:
            cv2.circle(visualized_image, (x1, y1), 1, (0, 255, 0), -1)
        # visualizer.frame = visualized_image
        return visualized_image
