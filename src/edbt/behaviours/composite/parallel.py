from enum import Enum

from edbt import BehaviourTree, Status

from .composite import Composite


class SuccessPolicy(Enum):
    REQUIRE_ONE = 0
    REQUIRE_ALL = 1


class Parallel(Composite):

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
                if (successes == need_successes or
                        self._success_policy is SuccessPolicy.REQUIRE_ONE):
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
