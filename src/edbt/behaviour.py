from abc import ABC, abstractmethod

from .observers import StatusObserver
from .status import Status


class Behaviour(ABC):

    def __init__(self):
        self.state = Status.INVALID
        self.observer: StatusObserver = None

    def tick(self) -> Status:
        if self.state == Status.INVALID:
            self._initialize()
        self.state = self._update()
        if self.state != Status.RUNNING:
            self._terminate()
        return self.state

    def reset(self) -> None:
        self.state = Status.INVALID
        self.observer = None

    @abstractmethod
    def _initialize(self) -> None:
        pass

    @abstractmethod
    def _update(self) -> Status:
        pass

    @abstractmethod
    def _terminate(self) -> None:
        pass

    def _abort(self) -> None:
        self.state = Status.ABORTED
