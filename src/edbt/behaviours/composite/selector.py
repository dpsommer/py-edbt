from edbt import Status

from .composite import Ordered


class Selector(Ordered):

    def _on_child_complete(self, status: Status):
        if status is Status.SUCCESS:
            self._tree.stop(self, status)
        else:
            try:
                next_child = next(self._children_iter)
                self._tree.start(next_child, self._on_child_complete)
            except StopIteration:
                self._tree.stop(self, Status.FAILURE)
