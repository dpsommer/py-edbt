from typing import Callable

from edbt import (
    BehaviourTree,
    Behaviour,
    BlackboardCondition,
    Status,
)

from .decorator import Decorator

AbortRule = Callable[[Behaviour], None]


class BOD(Decorator):
    _key: str
    _condition: BlackboardCondition
    _abort_rule: AbortRule

    def __init__(
            self,
            tree: BehaviourTree,
            child: Behaviour,
            key: str,
            condition: BlackboardCondition,
            abort_rule: AbortRule):
        super().__init__(tree, child)
        self._key = key
        self._condition = condition
        self._abort_rule = abort_rule

    def initialize(self):
        self._tree.add_observer(self._key, self.on_receive_update)

    def update(self) -> Status:
        if self._condition(self._tree, self._key):
            self._tree.start(self._child, self.on_child_complete)
            return Status.RUNNING
        return Status.FAILURE

    def on_child_complete(self, status: Status) -> None:
        if status is Status.SUCCESS:
            self.state = status
        else:
            self.state = Status.FAILURE

    def on_receive_update(self, value) -> None:
        if value is not None:
            if self._abort_rule:
                self._abort_rule(self)
            self._tree.remove_observer(self._key, self.on_receive_update)
