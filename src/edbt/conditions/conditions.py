from abc import abstractmethod

import edbt
from edbt import blackboard


class Condition(edbt.Behaviour):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def _update(self):
        return edbt.Status.SUCCESS if self() else edbt.Status.FAILURE


class HasValue(Condition):
    def __init__(self, key: str, namespace: str = None):
        super().__init__()
        self._key = key
        self._namespace = namespace

    def __call__(self, *args, **kwargs):
        return blackboard.read(self._key, self._namespace) is not None


class IsEqual(Condition):
    def __init__(self, key: str, value, namespace: str = None):
        super().__init__()
        self._key = key
        self._value = value
        self._namespace = namespace

    def __call__(self, *args, **kwargs):
        return blackboard.read(self._key, self._namespace) == self._value


__all__ = ["Condition", "HasValue", "IsEqual"]
