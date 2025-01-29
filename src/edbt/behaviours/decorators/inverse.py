from edbt import Status

from .decorator import Decorator


class Inverse(Decorator):
    def _update(self) -> Status:
        s = self.child.tick()
        if s is Status.RUNNING:
            return s
        elif s is Status.SUCCESS:
            return Status.FAILURE
        return Status.SUCCESS
