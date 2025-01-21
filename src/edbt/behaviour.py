from abc import ABC, abstractmethod

from .observers import StatusObserver
from .status import Status


class Behaviour(ABC):

    def __init__(self):
        self.state = Status.INVALID
        self.observer: StatusObserver = None

    def tick(self) -> Status:
        if self.state != Status.RUNNING:
            self.initialize()
        self.state = self.update()
        if self.state != Status.RUNNING:
            self.terminate()
        return self.state

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def update(self) -> Status:
        pass

    @abstractmethod
    def terminate(self) -> None:
        pass

    def abort(self) -> None:
        self.state = Status.ABORTED
