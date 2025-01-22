from edbt import (
    AbortRule,
    Behaviour,
    Status,
)

from .composite import Composite


class LowerPriority(AbortRule):
    parent: Composite

    def stop_on_complete(self, s: Status):
        self.parent._tree.stop(self.parent, s)

    def __call__(self, b: Behaviour):
        found = False

        for child in self.parent.children:
            if found and child.state == Status.RUNNING:
                self.parent._tree.abort(child)
            if child == b:
                found = True
                self.parent._tree.start(b, self.stop_on_complete)

__all__ = [
    "LowerPriority",
]
