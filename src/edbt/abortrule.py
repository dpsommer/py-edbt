from abc import ABC, abstractmethod

from .behaviour import Behaviour


class AbortRule(ABC):

    def __init__(self, parent: Behaviour):
        super().__init__()
        self.parent = parent

    @abstractmethod
    def __call__(self, b: Behaviour):
        pass
