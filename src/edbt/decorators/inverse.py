from edbt import Status

from .decorator import Decorator


class Inverse(Decorator):
    """Inverts the result of the decorated child

    If the child is RUNNING, has no effect. Otherwise, SUCCESS status becomes
    FAILURE, any other status is returned as SUCCESS.
    """

    def _update(self) -> Status:
        s = self.child.tick()
        if s is Status.RUNNING:
            return s
        elif s is Status.SUCCESS:
            return Status.FAILURE
        return Status.SUCCESS
