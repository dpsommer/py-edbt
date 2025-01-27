from typing import Any, Callable
from collections import defaultdict
from collections.abc import MutableMapping

BlackboardObserver = Callable[[Any], None]


# TODO: localized states for individual BTs?
class Blackboard(MutableMapping):

    def __init__(self, *args, **kwargs):
        self._values = dict()
        self._observers = defaultdict(set)
        self.update(dict(*args, **kwargs))

    def add_observer(self, key: str, obs: BlackboardObserver):
        self._observers[key].add(obs)

    def remove_observer(self, key: str, obs: BlackboardObserver):
        try:
            self._observers[key].remove(obs)
        except KeyError:
            pass  # noop if key or obs aren't in the map

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        self._values[key] = value
        self._run_observers(key, value)

    def __delitem__(self, key):
        del self._values[key]
        self._run_observers(key)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def _run_observers(self, key, value=None):
        if key in self._observers:
            # make a copy of the observer set here with list
            # as the callback may modify the set
            for o in list(self._observers[key]):
                if o is not None:
                    o(value)

blackboard = Blackboard()

__all__ = ["blackboard", "BlackboardObserver"]
