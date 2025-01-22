from abc import ABC, abstractmethod

from .tree import BehaviourTree


class Condition(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class _HasValue(Condition):
    def __call__(self, tree: BehaviourTree, key: str, *args, **kwargs):
        return (key in tree.blackboard.values
                    and tree.blackboard.values[key] != None)


class _IsEqual(Condition):
    def __call__(self, tree: BehaviourTree, key: str, value, *args, **kwargs):
        return (key in tree.blackboard.values
                    and tree.blackboard.values[key] == value)

HasValue = _HasValue()
IsEqual = _IsEqual()

__all__ = [
    "Condition",
    "HasValue",
    "IsEqual",
]
