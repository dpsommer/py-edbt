import edbt


class Decorator(edbt.Behaviour):
    """Decorator node superclass

    Defines common behaviour for Decorator nodes.

    Args:
        child (edbt.Behaviour, optional): child node. Defaults to None.
    """

    def __init__(self, child: edbt.Behaviour = None):
        super().__init__()
        self.child = child

    def reset(self):
        super().reset()
        self.child.reset()
