from typing import List
import numpy as np
from processing.optical_flow import SparseResult


class BaseInference:
    def infer(self, result):
        raise NotImplementedError()

    def get_title_message(self):
        return self.__class__.__name__

    def get_parameter_message(self):
        return self.__class__.__name__


class BaseSparseInference(BaseInference):
    def infer(self, result: SparseResult) -> List[np.ndarray[np.float64]]:
        raise NotImplementedError()
