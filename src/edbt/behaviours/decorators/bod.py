from typing import Type

from edbt import (
    AbortRule,
    BehaviourTree,
    Behaviour,
    Condition,
    Status,
)

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
        self._tree.add_observer(self._key, self._on_receive_update)

    def _update(self) -> Status:
        if self._condition(self._tree, self._key, self._value):
            self._tree.start(self.child, self._on_child_complete)
            return Status.RUNNING
        return Status.FAILURE

    def _on_child_complete(self, status: Status) -> None:
        if status is Status.SUCCESS:
            self.state = status
        else:
            self.state = Status.FAILURE

    def _on_receive_update(self, value) -> None:
        if value is not None:
            if self._abort_rule:
                self._abort_rule(self)
            self._tree.remove_observer(self._key, self._on_receive_update)
