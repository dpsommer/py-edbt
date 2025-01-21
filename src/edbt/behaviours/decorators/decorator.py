from edbt import BehaviourTree, Behaviour


class Decorator(Behaviour):

    def __init__(self, tree: BehaviourTree, child: Behaviour):
        self._tree = tree
        self._child = child

    def terminate(self) -> None: pass
    def abort(self) -> None: pass
