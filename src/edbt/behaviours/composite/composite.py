from abc import abstractmethod
from typing import List, Iterator

from edbt import (
    BehaviourTree,
    Behaviour,
    Status,
    StatusObserver,
)


class Composite(Behaviour):

    def __init__(self, tree: BehaviourTree):
        super().__init__()
        self._tree = tree
        self._children: List[Behaviour] = []

    def update(self):
        return Status.RUNNING

    def terminate(self): pass
    def abort(self): pass

    @abstractmethod
    def on_child_complete(self, status: Status):
        pass

    def add_child(self, child: Behaviour):
        self._children.append(child)

    def remove_child(self, child: Behaviour):
        # XXX: handle the ValueError here?
        self._children.remove(child)

    def clear_children(self):
        self._children.clear()

    # abort rules
    def lower_priority(self, o: StatusObserver):
        found = False

        for child in self._children:
            if found and child.state == Status.RUNNING:
                self._tree.abort(child)
            if child == self:
                found = True
                self._tree.start(self, o)


class Ordered(Composite):

    def __init__(self, tree):
        super().__init__(tree)
        self._children_iter: Iterator[Behaviour] = None

    def initialize(self):
        if len(self._children) > 0:
            self._children_iter = iter(self._children)
            first_child = next(self._children_iter)
            self._tree.start(first_child, self.on_child_complete)

    def abort(self):
        self.state = Status.ABORTED
        for child in self._children:
            if child.state == Status.RUNNING:
                self._tree.abort(child)
