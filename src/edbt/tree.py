from .behaviour import Behaviour
from .status import Status


class BehaviourTree:

    def __init__(self, root: Behaviour):
        """Constructs a Behaviour Tree with the given root

        Branch and leaf nodes extend from the child or children of the root
        node. When `tick` is called, walks from the root until a leaf node is
        reached and propagates the result back up the tree to be returned.

        Args:
            root (Behaviour): root node of the Behaviour Tree
        """
        self.root = root

    def tick(self) -> Status:
        return self.root.tick()


__all__ = ["BehaviourTree"]
