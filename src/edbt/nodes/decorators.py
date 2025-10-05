from edbt import Behaviour, Status, blackboard
from edbt.rules import AbortRule, Condition, HasValue, LowerPriority


class Decorator(Behaviour):
    """Decorator node superclass

    Defines common behaviour for Decorator nodes.

    Args:
        child (Behaviour, optional): child node. Defaults to None.
    """

    def __init__(self, child: Behaviour = None):
        super().__init__()
        self.child = child

    def reset(self):
        super().reset()
        self.child.reset()


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


class BOD(Decorator):
    """Blackboard Observer Decorator node

    Adds a dynamic observer to a blackboard key in a given namespace.

    When ticked, checks the defined Condition. If it is satisfied, ticks
    the child node. Reevaluates the abort condition when the observed key
    is modified.

    Args:
        key (str): blackboard key to observe
        condition (Condition): boolean Condition evaluated on tick
        namespace (str, optional): blackboard namespace. Defaults to None,
            which will write to the global default blackboard.
        child (Behaviour, optional): child node. Defaults to None.
        abort_rule (AbortRule, optional): conditional rule which aborts
            child execution if met. Defaults to None.
    """

    def __init__(
        self,
        key: str,
        condition: Condition,
        namespace: str = None,
        child: Behaviour = None,
        abort_rule: AbortRule = None,
    ):
        super().__init__(child)
        self._blackboard = blackboard.get_blackboard(namespace)
        self._key = key
        self._condition = condition
        self._abort_rule = abort_rule

    def _initialize(self):
        self._blackboard.add_observer(self._key, self._on_key_updated)

    def _update(self) -> Status:
        if self._condition():
            return self.child.tick()
        return Status.FAILURE

    def _on_key_updated(self, value) -> None:
        if value is not None and self._condition():
            if self._abort_rule:
                self._abort_rule(self)
            self._blackboard.remove_observer(self._key, self._on_key_updated)


class RequestHandler(BOD):

    def __init__(
        self,
        key: str,
        parent: Behaviour,
        namespace: str = None,
        child: Behaviour = None,
    ):
        super().__init__(
            key=key,
            child=child,
            namespace=namespace,
            condition=HasValue(key, namespace),
            abort_rule=LowerPriority(parent),
        )


__all__ = [
    "Decorator",
    "Inverse",
    "BOD",
    "RequestHandler",
]
