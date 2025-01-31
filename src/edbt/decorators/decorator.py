import edbt


class Decorator(edbt.Behaviour):

    def __init__(self, child: edbt.Behaviour=None):
        super().__init__()
        self.child = child

    def reset(self):
        super().reset()
        self.child.reset()
