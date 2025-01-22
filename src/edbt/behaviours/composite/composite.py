from abc import abstractmethod
from typing import List, Iterator

from edbt import (
    BehaviourTree,
    Behaviour,
    Status,
)


class Composite(Behaviour):

    def __init__(self, tree: BehaviourTree):
        super().__init__()
        self._tree = tree
        self._children: List[Behaviour] = []

    @property
    def children(self):
        # return a copy of the list to avoid mutation
        # except through the dedicated methods
        return list(self._children)

    def _update(self):
        return Status.RUNNING

    def _terminate(self): pass
    def _abort(self): pass

    @abstractmethod
    def _on_child_complete(self, status: Status):
        pass

    def add_child(self, child: Behaviour):
        self._children.append(child)

    def remove_child(self, child: Behaviour):
        # XXX: handle the ValueError here?
        self._children.remove(child)

    def clear_children(self):
        self._children.clear()


class Ordered(Composite):

    def __init__(self, tree):
        super().__init__(tree)
        self._children_iter: Iterator[Behaviour] = None

    def _initialize(self):
        if len(self._children) > 0:
            self._children_iter = iter(self._children)
            first_child = next(self._children_iter)
            self._tree.start(first_child, self._on_child_complete)

    def _abort(self):
        self.state = Status.ABORTED
        for child in self._children:
            if child.state == Status.RUNNING:
                self._tree.abort(child)
