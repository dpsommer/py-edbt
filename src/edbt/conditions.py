from .tree import BehaviourTree

from typing import Callable

BlackboardCondition = Callable[[BehaviourTree, str], bool]


def has_value(tree: BehaviourTree, key: str) -> bool:
    return (key in tree.blackboard.values
                and tree.blackboard.values[key] != None)

__all__ = [
    "BlackboardCondition",
    "has_value",
]
