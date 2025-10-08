from abc import ABC, abstractmethod
from enum import Enum
from uuid import UUID, uuid4

"""Set to hold references to background async tasks to avoid them being GC'd"""
background_tasks = set()


class Status(Enum):
    """Enumeration of possible behaviour statuses

    SUCCESS, FAILURE, and RUNNING are propagated from leaf behaviour nodes to
    describe their state. These states inform the behaviour and response state
    of conditional or composite nodes above them in the tree.

    The INVALID status is used to represent error states, typically with
    misconfigured trees. The ABORTED status is applied by a dynamic observer
    node's AbortRule to halt the current behaviour.
    """

    INVALID = -1
    SUCCESS = 0
    FAILURE = 1
    RUNNING = 2
    ABORTED = 3


class Behaviour(ABC):
    """Base Behaviour class

    All branch and leaf nodes extend from this abstract superclass.
    """

    def __init__(self):
        self._id: UUID = uuid4()
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
        self._id: UUID = uuid4()
        self.root = root

    def tick(self) -> Status:
        """Behaviour tree entrypoint

        Ticks the root node, walking the tree until a leaf node is reached.

        Returns:
            Status: the status propagated from the selected behaviour.
        """
        return self.root.tick()


__all__ = [
    "background_tasks",
    "Behaviour",
    "BehaviourTree",
    "Status",
]
