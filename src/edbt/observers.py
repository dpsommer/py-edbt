from typing import Any, Callable

from .status import Status

StatusObserver = Callable[[Status], None]
BlackboardObserver = Callable[[Any], None]

__all__ = [
    "StatusObserver",
    "BlackboardObserver",
]
