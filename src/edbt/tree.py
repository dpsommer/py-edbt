from .behaviour import Behaviour
from .status import Status


class BehaviourTree:

    def __init__(self, root: Behaviour):
        self.root = root
        self._mailbox = []

    def tick(self) -> Status:
        return self.root.tick()

__all__ = ["BehaviourTree"]
