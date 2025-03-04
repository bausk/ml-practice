from typing import List
import cv2
import numpy as np

from postprocessing.image_hud import ImageHUD
from processing.optical_flow import SparseResult


class IdentityHUD:
    def draw_mask(self, visualizer: ImageHUD, _: SparseResult | List[SparseResult]):
        return visualizer.frame


class SparseLinesHUD:
    def __init__(self, color=None):
        self.mask = None
        if color is None:
            color = np.random.randint(0, 255, (1, 3))[0]
        colors = np.zeros((20, 3))
        for i in range(20):
            colors[i] = color * (0.9 ** i)
        self.colors = colors.astype(int)

    def draw_mask(self, visualizer: ImageHUD, result: SparseResult):
        from_pixels, to_pixels = result.old_pixels, result.new_pixels
        if self.mask is None:
            self.mask = np.zeros_like(visualizer.frame)
        for i, (old_point, new_point) in enumerate(zip(from_pixels, to_pixels)):
            a, b = new_point.ravel()
            c, d = old_point.ravel()
            color = self.colors[i % len(self.colors)].tolist()
            self.mask = cv2.line(self.mask, (int(a), int(b)), (int(c), int(d)), color, 2)
            visualizer.frame = cv2.circle(visualizer.frame, (int(a), int(b)), 5, color, -1)
        visualized_image = cv2.add(visualizer.frame, self.mask)
        # visualizer.frame = visualized_image
        return visualized_image
