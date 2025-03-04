from typing import List
import cv2

from processing.optical_flow import IOpticalFlow, LucasKanadeOpticalFlow, SparseResult


class GenerationalLKFlow(IOpticalFlow):
    def __init__(self, OpticalFlowClass, max_frame_interval=600, max_active_generations=3):
        self.OpticalFlowClass = OpticalFlowClass
        self.flow_processors: List[LucasKanadeOpticalFlow | None] = []
        self.starting_frames = []
        self.frame_count = 0
        self.max_frame_interval = max_frame_interval
        self.max_active_generations = max_active_generations
        return super().__init__()

    def set1stFrame(self, frame):
        self.first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def _is_new_processor_to_instantiate(self):
        try:
            latest_instantiation_frame = self.starting_frames[-1]
            if self.frame_count - latest_instantiation_frame > self.max_frame_interval:
                return True
        except IndexError:
            return True
        return False

    def _instantiate_new_processor(self):
        new_processor: LucasKanadeOpticalFlow = self.OpticalFlowClass()
        self.flow_processors.append(new_processor)
        self.starting_frames.append(self.frame_count)
        active_processors_count = len(list(filter(lambda x: x is not None, self.flow_processors)))
        if active_processors_count > self.max_active_generations:
            for i, processor in enumerate(self.flow_processors):
                if processor is None:
                    continue
                self._destroy_processor(i)
                break

    def _destroy_processor(self, i):
        processor_to_release = self.flow_processors[i]
        self.flow_processors[i] = None
        del processor_to_release

    def apply(self, frame):
        if self._is_new_processor_to_instantiate():
            self._instantiate_new_processor()

        results: List[SparseResult | None] = []
        for i, processor in enumerate(self.flow_processors):
            try:
                if processor is None:
                    results.append(None)
                    continue
                _, sparse_result = processor.apply(frame)
                results.append(sparse_result)
            except cv2.error:
                results.append(None)
                self._destroy_processor(i)

        self.frame_count += 1
        return frame, results
