from edbt import (
    BehaviourTree,
    Behaviour,
)

from .bod import BOD
from .abortrules import LowerPriority
from ..conditions import HasValue


class RequestHandler(BOD):

    def __init__(
            self,
            tree: BehaviourTree,
            parent: Behaviour,
            key: str,
            child: Behaviour=None):
        super().__init__(
            tree=tree,
            parent=parent,
            condition=HasValue,
            key=key,
            child=child,
            abort_rule=LowerPriority,
        )
