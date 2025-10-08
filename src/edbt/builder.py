from typing import List, Type

from edbt import Behaviour, BehaviourTree
from edbt.nodes import (
    BOD,
    Composite,
    Decorator,
    Inverse,
    Parallel,
    RequestHandler,
    Selector,
    Sequencer,
)
from edbt.rules import AbortRule, Condition


class TreeBuilderException(Exception):
    """Exception type to capture errors from the TreeBuilder class."""


class TreeBuilder:
    """Builder for `BehaviourTree` objects.

    Simplifies the creation of complex and nested behaviour trees with
    helper functions for both common and custom nodes.

    Note that the build function requires an async context to run.

    Examples:
        Note that the actions used below are for example purposes only and
        are not part of the library.

        >>> get_drink_from_fridge = (
        >>>     TreeBuilder()
        >>>         .sequencer()
        >>>             .leaf(OpenFridge())
        >>>             .selector()
        >>>                 .leaf(GrabDrink())
        >>>                 .leaf(CloseFridge())
        >>>                 .done()
        >>>             .leaf(CloseFridge())
        >>>         .build())
    """

    def __init__(self):
        self._root = None
        self._composites: List[Composite] = []
        self._decorator: Decorator = None

    def _insert(self, b: Behaviour) -> "TreeBuilder":
        if self._root is None:
            self._root = b
        elif self._decorator:
            self._decorator.child = b
            self._decorator = None
        elif self._composites:
            self._composites[-1].add_child(b)
        else:
            raise TreeBuilderException(
                f"failed to insert behaviour {b}: no suitable parent"
            )

        return self

    def _composite(self, c) -> "TreeBuilder":
        self._insert(c)
        self._composites.append(c)
        return self

    def add_subtree(self, subtree: BehaviourTree) -> "TreeBuilder":
        self._insert(subtree.root)
        return self

    def selector(self) -> "TreeBuilder":
        """Adds a Selector node to the tree.

        Nested Composite nodes can be closed with `done()` to resume insertion
        from the nearest composite ancestor.
        """
        return self._composite(Selector())

    def sequencer(self) -> "TreeBuilder":
        """Adds a Sequencer node to the tree.

        Nested Composite nodes can be closed with `done()` to resume insertion
        from the nearest composite ancestor.
        """
        return self._composite(Sequencer())

    def parallel(self) -> "TreeBuilder":
        """Adds a Parallel node to the tree.

        Nested Composite nodes can be closed with `done()` to resume insertion
        from the nearest composite ancestor.
        """
        return self._composite(Parallel())

    def done(self) -> "TreeBuilder":
        """Closes the most recent composite node"""
        if len(self._composites) == 0:
            raise TreeBuilderException("done() called with no composite ancestor")
        self._composites.pop()
        return self

    def decorator(self, d: Decorator) -> "TreeBuilder":
        """Adds the given Decorator node to the tree.

        The next node in the tree will be added as its child.
        """
        self._insert(d)
        self._decorator = d
        return self

    def inverse(self) -> "TreeBuilder":
        """Adds an inverse Decorator node to the tree.

        Inverts the child's status response - Status.RUNNING remains the same,
        Status.SUCCESS becomes Status.FAILURE, and any other response becomes
        Status.SUCCESS. The next node in the tree will be added as its child.
        """
        self.decorator(Inverse())
        return self

    def blackboard_observer(
        self,
        key: str,
        condition: Condition,
        abort_rule: Type[AbortRule] = None,
        namespace: str = None,
    ) -> "TreeBuilder":
        """Adds a BOD (Blackboard Observer Decorator) node to the tree.

        The next node in the tree will be added as its child.
        """
        if not self._composites and abort_rule:
            raise TreeBuilderException("blackboard observer has no composite ancestor")
        return self.decorator(
            BOD(
                key=key,
                namespace=namespace,
                condition=condition,
                abort_rule=abort_rule(self._composites[-1]),
            )
        )

    def request_handler(self, key: str, namespace: str = None) -> "TreeBuilder":
        """Adds a RequestHandler node to the tree.

        The next node in the tree will be added as its child.
        """
        if not self._composites:
            raise TreeBuilderException("request handler has no composite ancestor")
        return self.decorator(
            RequestHandler(key=key, parent=self._composites[-1], namespace=namespace)
        )

    def leaf(self, behaviour: Behaviour) -> "TreeBuilder":
        """Adds the given behaviour to the tree as a leaf node."""
        return self._insert(behaviour)

    def _validate(self):
        if self._root is None:
            raise TreeBuilderException("can't build an empty tree")
        if self._decorator is not None:
            raise TreeBuilderException("build called before adding child to decorator")

    def build(self) -> BehaviourTree:
        """Build and return the behaviour tree.

        Returns:
            BehaviourTree: the `BehaviourTree` object defined by the builder.
        """
        self._validate()
        return BehaviourTree(self._root)


__all__ = ["TreeBuilder", "TreeBuilderException"]
