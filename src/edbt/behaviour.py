from abc import ABC, abstractmethod

from .status import Status


class Behaviour(ABC):

    def __init__(self):
        """Base Behaviour class

        All branch and leaf nodes extend from this abstract superclass.
        """
        self.state = Status.INVALID

    def tick(self) -> Status:
        if self.state != Status.RUNNING:
            self._initialize()
        self.state = self._update()
        if self.state != Status.RUNNING:
            self._terminate()
        return self.state

    def reset(self) -> None:
        self.state = Status.INVALID

    def _initialize(self) -> None:
        # the linter complains about empty non-abstract
        # function here if this is pass, so just return
        return

    @abstractmethod
    def _update(self) -> Status:
        pass

    def _terminate(self) -> None:
        return

    def abort(self) -> None:
        self.state = Status.ABORTED


__all__ = ["Behaviour"]
