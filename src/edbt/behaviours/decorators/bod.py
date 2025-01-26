from typing import Type

from edbt import (
    BehaviourTree,
    Behaviour,
    Condition,
    Status,
)

from .abortrules import AbortRule
from .decorator import Decorator


class BOD(Decorator):
    _key: str
    _condition: Condition
    _abort_rule: AbortRule

    def __init__(
            self,
            tree: BehaviourTree,
            parent: Behaviour,
            condition: Condition,
            key: str,
            value=None,
            child: Behaviour=None,
            abort_rule: Type[AbortRule]=None):
        super().__init__(tree, child)
        self._key = key
        self._value = value
        self._condition = condition
        self._abort_rule = abort_rule(parent) if abort_rule else None

    def _initialize(self):
        self._tree.add_observer(self._key, self._on_key_updated)

    def _update(self) -> Status:
        if self._condition(self._tree, self._key, self._value):
            return self.child.tick()
        return Status.FAILURE

    def _on_key_updated(self, value) -> None:
        if value is not None:
            if self._abort_rule:
                self._abort_rule(self)
            self._tree.remove_observer(self._key, self._on_key_updated)
