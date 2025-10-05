from edbt import Status

from .composite import Ordered


class Sequencer(Ordered):

    def _update(self) -> Status:
        while self.has_next_child():
            status = next(self).tick()
            if status != Status.SUCCESS:
                # move the index back one so we poll a
                # running child on subsequent ticks
                self._idx -= 1
                return status

        # all children were successful, so return SUCCESS
        return Status.SUCCESS
