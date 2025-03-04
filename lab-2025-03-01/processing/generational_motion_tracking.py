from typing import Callable, List
import numpy as np

from processing.optical_flow import SparseResult
from processing.base_tracking import BaseInference, BaseSparseInference


class GenerationalVectorInference(BaseInference):
    def __init__(self, TrackerInstantiator: Callable[[np.ndarray], BaseSparseInference]) -> None:
        self.TrackerInstantiator = TrackerInstantiator
        self.trackers: List[BaseSparseInference | None] = []
        self.active_trackers = 0
        self.fizzled_trackers = 0
        self.average_motion_vector = np.array([0.0, 0.0])
        self.initial_motion_vector = np.array([0.0, 0.0])

    def _synchronize_trackers_with_results(self, results: List[SparseResult | None]):
        for i, result in enumerate(results):
            # No result means process is not active anymore and its tracker should be removed
            if result is None:
                tracker_to_remove = self.trackers[i]
                if tracker_to_remove is not None:
                    self.trackers[i] = None
                    del tracker_to_remove
                    self.active_trackers -= 1
                    self.fizzled_trackers += 1
                continue
            # Instantiate new tracker for new results
            if len(self.trackers) <= i:
                new_tracker = self.TrackerInstantiator(self.average_motion_vector)
                self.trackers.append(new_tracker)
                self.active_trackers += 1

    def infer(self, results: List[SparseResult | None]):
        self._synchronize_trackers_with_results(results)
        
        subvector_results = []
        compound_motion_vector_results = []
        for i, result in enumerate(results):
            if result is None: # Tracker and its OF process are not active anymore
                subvector_results.append(None)
                continue
            tracker: BaseSparseInference = self.trackers[i]
            # One-generation tracker returns motion vector and initial vector
            result_vectors = tracker.infer(result)
            subvector_results.append(result_vectors)
            compound_motion_vector = result_vectors[0] + result_vectors[1]
            compound_motion_vector_results.append(compound_motion_vector)

        average_motion_vector = np.mean(np.array(compound_motion_vector_results), axis=0)
        self.average_motion_vector = average_motion_vector
        return {
            'average_motion_vector': average_motion_vector,
            'subvector_results': subvector_results
        }
    
    def get_title_message(self):
        return f'GEN {len(self.trackers)}'
    
    def get_parameter_message(self):
        return f'''ACTIVE: {self.active_trackers}
        \nFIZZLED: {self.fizzled_trackers}
        \nAVG: {self.average_motion_vector}
        '''
