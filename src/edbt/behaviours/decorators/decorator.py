from edbt import BehaviourTree, Behaviour


class Decorator(Behaviour):

    def __init__(self, child: Behaviour):
        super().__init__()
        self.child = child

    def reset(self):
        super().reset()
        self.child.reset()

    def _terminate(self) -> None: pass
