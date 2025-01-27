from edbt import Behaviour

from .bod import BOD
from .abortrules import LowerPriority
from ..conditions import HasValue


class RequestHandler(BOD):

    def __init__(self, key: str, child: Behaviour=None):
        super().__init__(
            condition=HasValue,
            key=key,
            child=child,
            abort_rule=LowerPriority,
        )
