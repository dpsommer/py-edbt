from edbt import Status

from .composite import Ordered


class Selector(Ordered):

    def _update(self) -> Status:
        while self._idx < len(self._children_iter):
            # FIXME: need to peek the child we last checked
            status = self._children_iter[self._idx].tick()
            if status in {Status.SUCCESS, Status.RUNNING}:
                return status
            self._idx += 1
        return Status.FAILURE
