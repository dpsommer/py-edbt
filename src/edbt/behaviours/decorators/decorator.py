from edbt import BehaviourTree, Behaviour


class Decorator(Behaviour):

    def __init__(self, tree: BehaviourTree, child: Behaviour):
        super().__init__()
        self._tree = tree
        self.child = child

    def _terminate(self) -> None: pass
    def _abort(self) -> None: pass
