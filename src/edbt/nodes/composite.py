from enum import Enum
from typing import List

from edbt import Behaviour, Status


class Composite(Behaviour):
    """Superclass for all composite nodes

    Composite nodes can have multiple descendants in the tree, and return a
    status based on the aggregate statuses of their children.
    """

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
    """Superclass for composite nodes with sequential execution"""

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


class Selector(Ordered):
    """Runs children in sequence, succeeding if any child succeeds

    Returns the status of its last child if none are successful.

    Waits for each child to complete before moving onto the next, returning
    a RUNNING status if the child is processing.
    """

    def _update(self) -> Status:
        status = Status.INVALID

        while self.has_next_child():
            status = next(self).tick()
            if status in {Status.SUCCESS, Status.RUNNING}:
                # move the index back one so we poll a
                # running child on subsequent ticks
                self._idx -= 1
                return status

        # return the status of the last failing child
        # or INVALID if there are no children
        return status


class Sequencer(Ordered):
    """Runs children in sequence, succeeding if all children succeed

    Otherwise returns the first non-SUCCESS status.

    Waits for each child to complete before moving onto the next, returning
    a RUNNING status if the child is processing.
    """

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


class SuccessPolicy(Enum):
    REQUIRE_ONE = 0
    REQUIRE_ALL = 1


class Parallel(Composite):
    """Runs children in parallel, succeeding based on success policy

    Returns a status based on the given `SuccessPolicy`. With REQUIRE_ONE,
    SUCCESS is returned once the first child returns SUCCESS. If no
    children succeed, returns FAILURE.

    With REQUIRE_ALL, SUCCESS is only returned if all children succeed.
    Returns FAILURE as soon as any child fails.

    Returns RUNNING if the status is indeterminate and any children are
    still running.

    Args:
        policy (SuccessPolicy): policy to determine when this node returns
            a SUCCESS status. One of REQUIRE_ONE or REQUIRE_ALL.
    """

    def __init__(self, policy: SuccessPolicy):
        super().__init__()
        self._success_policy = policy
        self._running_children = []

    def _initialize(self):
        super()._initialize()
        self._running_children = list(self.children)

    def _update(self) -> Status:
        # track success count and required number of successes for RequireAll
        # we only need len(runningNodes) successes each tick as we can imply that:
        # * if RequireOne, we haven't succeeded yet but any Success will be enough
        # * if RequireAll, completed tasks must have been Success as we fail fast
        successes = 0
        need_successes = len(self._running_children)
        still_running = []

        status = Status.FAILURE

        for child in self._running_children:
            s = child.tick()
            if s is Status.SUCCESS:
                successes += 1
                if (
                    successes == need_successes
                    or self._success_policy is SuccessPolicy.REQUIRE_ONE
                ):
                    return s
            elif s is Status.RUNNING:
                status = Status.RUNNING
                still_running.append(child)
            elif self._success_policy is SuccessPolicy.REQUIRE_ALL:
                return s

        if status is Status.RUNNING:
            self._running_children = still_running

        return status

    def _terminate(self):
        for child in self._children:
            if child.state is Status.RUNNING:
                child.abort()

    def abort(self):
        super().abort()
        self._terminate()


__all__ = [
    "Composite",
    "Selector",
    "Sequencer",
    "SuccessPolicy",
    "Parallel",
]
