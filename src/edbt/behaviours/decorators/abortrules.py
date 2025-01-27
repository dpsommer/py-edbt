from abc import ABC, abstractmethod

from edbt import Behaviour, Status

from ..composite import Composite


class AbortRule(ABC):

    def __init__(self, parent: Behaviour):
        super().__init__()
        self.parent = parent

    @abstractmethod
    def __call__(self, b: Behaviour):
        pass


class LowerPriority(AbortRule):
    parent: Composite

    def __call__(self, b: Behaviour):
        found = False

        for child in self.parent.children:
            if found and child.state == Status.RUNNING:
                # if a sibling to the right of the given
                # child is running, abort the parent so it
                # restarts on the next tick
                self.parent.abort()
                return
            if child == b:
                found = True
                child.tick()
