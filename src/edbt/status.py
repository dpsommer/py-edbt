from enum import Enum


class Status(Enum):
    INVALID = -1
    SUCCESS = 0
    FAILURE = 1
    RUNNING = 2
    ABORTED = 3


__all__ = ["Status"]
