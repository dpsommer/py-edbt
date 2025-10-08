from abc import ABC, abstractmethod

from edbt import Behaviour, Status
from edbt.nodes.composite import Composite


class AbortRule(ABC):
    """Callable to abort running behaviour

    Asynchronous nodes such as the BlackboardObserverDecorator require a
    mechanism to modify current behaviour in response to a change in state or
    a request from another agent.

    AbortRules are triggered conditionally by these nodes, and define logic to
    halt execution of their siblings or other running behaviours.

    Args:
        parent (Behaviour): the parent of the node this rule is associated with
    """

    def __init__(self, parent: Behaviour):
        super().__init__()
        self.parent = parent

    @abstractmethod
    def __call__(self, b: Behaviour) -> None:
        pass


class LowerPriority(AbortRule):
    """Aborts any running sibling to the right of the associated node"""

    parent: Composite

    def __call__(self, b: Behaviour) -> None:
        found = False

        for child in self.parent.children:
            if found and child.state == Status.RUNNING:
                # if a sibling to the right of the given
                # child is running, abort the parent so it
                # restarts on the next tick
                self.parent.abort()
                return
            if child == b:
                found = True
