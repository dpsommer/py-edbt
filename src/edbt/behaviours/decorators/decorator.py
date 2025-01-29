from edbt import Behaviour


class Decorator(Behaviour):

    def __init__(self, child: Behaviour=None):
        super().__init__()
        self.child = child

    def reset(self):
        super().reset()
        self.child.reset()

    def _initialize(self) -> None: pass
    def _terminate(self) -> None: pass
