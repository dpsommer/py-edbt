from abc import abstractmethod

from edbt import Behaviour, Status, blackboard


class Condition(Behaviour):
    """Boolean condition callable superclass to define conditional nodes

    When ticked, returns SUCCESS if the defined condition is true, otherwise
    returns FAILURE.

    Returns:
        bool: True if the condition passes, otherwise False.
    """

    @abstractmethod
    def __call__(self, *args, **kwargs) -> bool:
        pass

    def _update(self):
        return Status.SUCCESS if self() else Status.FAILURE


class HasValue(Condition):
    """Checks if a given blackboard key has a non-null value

    Args:
        key (str): the blackboard key to check
        namespace (str, optional): Optional blackboard namespace. Defaults
            to None, denoting the default global namespace.
    """

    def __init__(self, key: str, namespace: str = None):
        super().__init__()
        self._key = key
        self._namespace = namespace

    def __call__(self, *args, **kwargs) -> bool:
        return blackboard.read(self._key, self._namespace) is not None


class IsEqual(Condition):
    """Checks if a given blackboard key's value matches a provided value

    Args:
        key (str): the blackboard key to check
        value (any): the value to compare
        namespace (str, optional): Optional blackboard namespace. Defaults
            to None, denoting the default global namespace.
    """

    def __init__(self, key: str, value, namespace: str = None):
        super().__init__()
        self._key = key
        self._value = value
        self._namespace = namespace

    def __call__(self, *args, **kwargs) -> bool:
        return blackboard.read(self._key, self._namespace) == self._value


__all__ = ["Condition", "HasValue", "IsEqual"]
