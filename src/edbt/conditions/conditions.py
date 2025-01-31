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


class HasValue(Condition):
    def __init__(self, key: str):
        super().__init__()
        self._key = key

    def __call__(self, *args, **kwargs):
        return blackboard.get(self._key) != None


class IsEqual(Condition):
    def __init__(self, key: str, value):
        super().__init__()
        self._key = key
        self._value = value

    def __call__(self, *args, **kwargs):
        return blackboard.get(self._key) == self._value

__all__ = [
    "Condition",
    "HasValue",
    "IsEqual",
]
