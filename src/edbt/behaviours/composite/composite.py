from abc import abstractmethod
from typing import List

from edbt import (
    Behaviour,
    Status,
)


class Composite(Behaviour):

    def __init__(self):
        super().__init__()
        self._children: List[Behaviour] = []

    @property
    def children(self):
        # return a copy of the list to avoid mutation
        # except through the dedicated methods
        return list(self._children)

    def reset(self):
        super().reset()
        for child in self.children:
            child.reset()

    def _initialize(self):
        self.state = Status.RUNNING

    @abstractmethod
    def _update(self):
        pass

    def _terminate(self): pass

    def add_child(self, child: Behaviour):
        self._children.append(child)

    def remove_child(self, child: Behaviour):
        # XXX: handle the ValueError here?
        self._children.remove(child)

    def clear_children(self):
        self._children.clear()


class Ordered(Composite):

    def __init__(self):
        super().__init__()
        self._children_iter: List[Behaviour] = None
        self._idx = 0

    def _initialize(self):
        super()._initialize()
        if len(self._children) > 0:
            self._idx = 0
            self._children_iter = self.children

    def abort(self):
        super().abort()
        for child in self._children:
            if child.state == Status.RUNNING:
                child.abort()
