from typing import List, Type

from edbt import *


# TODO: builder pattern to simplify tree construction
# build from the bottom up
class TreeBuilder:
    def __init__(self):
        self._root = None
        self._composites: List[Composite] = []
        self._decorate: Decorator = None

    def _insert(self, b: Behaviour) -> "TreeBuilder":
        if self._root is None:
            self._root = b
        elif self._decorate:
            self._decorate.child = b
            self._decorate = None
        elif self._composites:
            self._composites[-1].add_child(b)

        return self

    def _composite(self, c) -> "TreeBuilder":
        self._insert(c)
        self._composites.append(c)
        return self

    def selector(self) -> "TreeBuilder":
        return self._composite(Selector())

    def sequencer(self) -> "TreeBuilder":
        return self._composite(Sequencer())

    def parallel(self) -> "TreeBuilder":
        return self._composite(Parallel())

    def done(self) -> "TreeBuilder":
        self._composites.pop()
        return self

    def _decorator(self, d: Decorator) -> "TreeBuilder":
        self._insert(d)
        self._decorate = d
        return self

    def blackboard_observer(self, key: str, condition: Condition, value=None,
                            abort: Type[AbortRule]=None) -> "TreeBuilder":
        if not self._composites and abort:
            raise "blackboard observer has no composite ancestor"
        return self._decorator(BOD(
            key=key,
            value=value,
            condition=condition,
            abort_rule=abort(self._composites[-1]),
        ))

    def request_handler(self, key) -> "TreeBuilder":
        if not self._composites:
            raise "request handler has no composite ancestor"
        return self._decorator(RequestHandler(key, self._composites[-1]))

    def leaf(self, behaviour: Behaviour) -> "TreeBuilder":
        return self._insert(behaviour)

    def build(self) -> BehaviourTree:
        return BehaviourTree(self._root)
