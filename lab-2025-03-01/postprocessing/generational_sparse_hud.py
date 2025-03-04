from typing import List
import cv2
import numpy as np

from postprocessing.image_hud import ImageHUD
from processing.optical_flow import SparseResult


class IdentityHUD:
    def draw(self, visualizer: ImageHUD, _: SparseResult | List[SparseResult]):
        return visualizer.frame


class GenerationalSparseHUD:
    def __init__(self, palette=None):
        self.mask = None
        self.color_palettes = []
        self.has_subvector_capacity = True
        if palette is None:
            palette = [
                np.random.randint(0, 255, (1, 3))[0] for _ in range(10)
            ]

        # By default, form 10 palettes of 20 colors each
        # to be used in a round-robin fashion to visualize generations
        # of sparse optical flow results
        for color in palette:
            colors = np.zeros((20, 3))
            for i in range(20):
                colors[i] = color * (0.9 ** i)
            self.color_palettes.append(colors.astype(int))

    def draw_mask(self, visualizer: ImageHUD, results: List[SparseResult | None]):
        if self.mask is None:
            self.mask = np.zeros_like(visualizer.frame)
        for i, result in enumerate(results):
            if result is None:
                continue
            current_palette = self.color_palettes[i % len(self.color_palettes)]
            from_pixels, to_pixels = result.old_pixels, result.new_pixels
            for i, (old_point, new_point) in enumerate(zip(from_pixels, to_pixels)):
                a, b = new_point.ravel()
                c, d = old_point.ravel()
                color = current_palette[i % len(current_palette)].tolist()
                # self.mask = cv2.line(self.mask, (int(a), int(b)), (int(c), int(d)), color, 2)
                visualizer.frame = cv2.circle(visualizer.frame, (int(a), int(b)), 5, color, -1)
        visualized_image = cv2.add(visualizer.frame, self.mask)
        return visualized_image

    # def draw_subvectors(self, visualizer: ImageHUD, subvector_generations: List[List[SparseResult] | None]):
    #     # Incorrect implementation, change this
    #     if self.mask is None:
    #         self.mask = np.zeros_like(visualizer.frame)
    #     for i, result in enumerate(results):
    #         if result is None:
    #             continue
    #         current_palette = self.color_palettes[i % len(self.color_palettes)]
    #         from_pixels, to_pixels = result.old_pixels, result.new_pixels
    #         for i, (old_point, new_point) in enumerate(zip(from_pixels, to_pixels)):
    #             a, b = new_point.ravel()
    #             c, d = old_point.ravel()
    #             color = current_palette[i % len(current_palette)].tolist()
    #             self.mask = cv2.line(self.mask, (int(a), int(b)), (int(c), int(d)), color, 2)
    #             visualizer.frame = cv2.circle(visualizer.frame, (int(a), int(b)), 5, color, -1)
    #     visualized_image = cv2.add(visualizer.frame, self.mask)
    #     return visualized_image