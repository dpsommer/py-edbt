from abc import abstractmethod

from edbt import blackboard, Behaviour, Status


class Condition(Behaviour):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def _initialize(self):
        pass

    def _update(self):
        return Status.SUCCESS if self() else Status.FAILURE

    def _terminate(self):
        pass


class _HasValue(Condition):
    def __call__(self, key: str, *args, **kwargs):
        return blackboard.get(key) != None


class _IsEqual(Condition):
    def __call__(self, key: str, value, *args, **kwargs):
        return blackboard.get(key) == value

HasValue = _HasValue()
IsEqual = _IsEqual()

__all__ = [
    "Condition",
    "HasValue",
    "IsEqual",
]
