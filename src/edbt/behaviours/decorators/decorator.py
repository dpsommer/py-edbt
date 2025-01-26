from edbt import BehaviourTree, Behaviour


class Decorator(Behaviour):

    def __init__(self, tree: BehaviourTree, child: Behaviour):
        super().__init__()
        self._tree = tree
        self.child = child

    def reset(self):
        super().reset()
        self.child.reset()

    def _terminate(self) -> None: pass
