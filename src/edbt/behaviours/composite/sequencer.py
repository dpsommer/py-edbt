from edbt import Status

from .composite import Ordered


class Sequencer(Ordered):

    def _update(self) -> Status:
        while self._idx < len(self._children_iter):
            status = self._children_iter[self._idx].tick()
            if status != Status.SUCCESS:
                return status
            self._idx += 1
        return Status.SUCCESS
