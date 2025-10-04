import edbt
from edbt import blackboard

from ..conditions import Condition
from .abortrules import AbortRule
from .decorator import Decorator


class BOD(Decorator):

    def __init__(
        self,
        key: str,
        condition: Condition,
        namespace: str = None,
        child: edbt.Behaviour = None,
        abort_rule: AbortRule = None,
    ):
        super().__init__(child)
        self._blackboard = blackboard.get_blackboard(namespace)
        self._key = key
        self._condition = condition
        self._abort_rule = abort_rule

    def _initialize(self):
        self._blackboard.add_observer(self._key, self._on_key_updated)

    def _update(self) -> edbt.Status:
        if self._condition():
            return self.child.tick()
        return edbt.Status.FAILURE

    def _on_key_updated(self, value) -> None:
        if value is not None and self._condition():
            if self._abort_rule:
                self._abort_rule(self)
            self._blackboard.remove_observer(self._key, self._on_key_updated)
