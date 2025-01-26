from enum import Enum

from edbt import BehaviourTree, Status

from .composite import Composite


class SuccessPolicy(Enum):
    REQUIRE_ONE = 0
    REQUIRE_ALL = 1


class Parallel(Composite):

    def __init__(self, tree: BehaviourTree, policy: SuccessPolicy):
        super().__init__(tree)
        self._success_policy = policy
        self._successes = 0
        self._failures = 0

    def _initialize(self):
        super()._initialize()
        self._successes = 0
        self._failures = 0
        for child in self._children:
            self._tree.start(child, self._on_child_complete)

    def _on_child_complete(self, status: Status):
        if status is Status.SUCCESS:
            self._successes += 1
            if (self._success_policy is SuccessPolicy.REQUIRE_ONE
                    or self._successes == len(self._children)):
                self._tree.stop(self, status)
        else:
            self._failures += 1
            if (self._success_policy is SuccessPolicy.REQUIRE_ALL
                    or self._failures == len(self._children)):
                self._tree.stop(self, Status.FAILURE)

        if (self.state is not Status.RUNNING
                and self._successes + self._failures < len(self._children)):
            self._terminate()

    def _terminate(self):
        for child in self._children:
            if child.state is Status.RUNNING:
                self._tree.abort(child)

    def _abort(self):
        super()._abort()
        self._terminate()
