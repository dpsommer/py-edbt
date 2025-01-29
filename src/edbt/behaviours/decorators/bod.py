from edbt import (
    blackboard,
    Behaviour,
    Status,
)

from .abortrules import AbortRule
from .decorator import Decorator
from ..conditions import Condition


class BOD(Decorator):
    _key: str
    _condition: Condition
    _abort_rule: AbortRule

    def __init__(
            self,
            key: str,
            condition: Condition,
            child: Behaviour=None,
            abort_rule: AbortRule=None):
        super().__init__(child)
        self._key = key
        self._condition = condition
        self._abort_rule = abort_rule

    def _initialize(self):
        blackboard.add_observer(self._key, self._on_key_updated)

    def _update(self) -> Status:
        if self._condition():
            status = self.child.tick()
            return status
        return Status.FAILURE

    def _on_key_updated(self, value) -> None:
        if value is not None and self._condition():
            if self._abort_rule:
                self._abort_rule(self)
            blackboard.remove_observer(self._key, self._on_key_updated)
