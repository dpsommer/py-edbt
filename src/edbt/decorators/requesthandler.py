import edbt

from ..conditions import HasValue
from .abortrules import LowerPriority
from .bod import BOD


class RequestHandler(BOD):

    def __init__(
        self,
        key: str,
        parent: edbt.Behaviour,
        namespace: str = None,
        child: edbt.Behaviour = None,
    ):
        super().__init__(
            key=key,
            child=child,
            namespace=namespace,
            condition=HasValue(key, namespace),
            abort_rule=LowerPriority(parent),
        )
