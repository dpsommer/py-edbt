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
        # except through internal methods
        return list(self._children)

    def reset(self):
        super().reset()
        for child in self._children:
            child.reset()

    def _initialize(self):
        self.state = Status.RUNNING

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
        self._idx = 0

    def _initialize(self):
        super()._initialize()
        if len(self._children) > 0:
            self._reset_iter()

    def abort(self):
        super().abort()
        for child in self._children:
            if child.state == Status.RUNNING:
                child.abort()
        # move the index so we exit the update loop after abort is called
        self._idx = len(self._children)

    def reset(self):
        super().reset()
        self._reset_iter()

    def has_next_child(self):
        return self._idx < len(self._children)

    def _reset_iter(self):
        self._idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.has_next_child():
            raise StopIteration()
        next_child = self._children[self._idx]
        self._idx += 1
        return next_child
