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
                self.parent._tree.abort(child)
            if child == b:
                found = True
                self.parent._tree.start(b)
