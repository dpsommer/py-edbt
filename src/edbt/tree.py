from abc import ABC, abstractmethod

from .const import Status

"""Set to hold references to background async tasks"""
background_tasks = set()


class Behaviour(ABC):
    """Base Behaviour class

    All branch and leaf nodes extend from this abstract superclass.
    """

    def __init__(self):
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


class BehaviourTree:
    """Constructs a Behaviour Tree with the given root

    Branch and leaf nodes extend from the child or children of the root
    node. When `tick` is called, walks from the root until a leaf node is
    reached and propagates the result back up the tree to be returned.

    Args:
        root (Behaviour): root node of the Behaviour Tree
    """

    def __init__(self, root: Behaviour):
        self.root = root

    def tick(self) -> Status:
        return self.root.tick()


__all__ = [
    "background_tasks",
    "Behaviour",
    "BehaviourTree",
]
