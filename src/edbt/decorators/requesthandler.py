import edbt

from .bod import BOD
from .abortrules import LowerPriority
from ..conditions import HasValue


class RequestHandler(BOD):

    def __init__(self, key: str, parent: edbt.Behaviour,
                 namespace: str=None, child: edbt.Behaviour=None):
        super().__init__(
            key=key,
            child=child,
            namespace=namespace,
            condition=HasValue(key, namespace),
            abort_rule=LowerPriority(parent),
        )
