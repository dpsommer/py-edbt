from edbt import Status

from .composite import Ordered


class Sequencer(Ordered):

    def on_child_complete(self, status: Status):
        if status is Status.SUCCESS:
            try:
                next_child = next(self._children_iter)
                self._tree.start(next_child, self.on_child_complete)
            except StopIteration:
                self._tree.stop(self, status)
        else:
            self._tree.stop(self, Status.FAILURE)
