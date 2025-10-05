from edbt import Status

from .composite import Ordered


class Selector(Ordered):

    def _update(self) -> Status:
        status = None

        while self.has_next_child():
            status = next(self).tick()
            if status in {Status.SUCCESS, Status.RUNNING}:
                # move the index back one so we poll a
                # running child on subsequent ticks
                self._idx -= 1
                return status

        # return the status of the last failing child
        # or INVALID if there are no children
        return status or Status.INVALID
