from edbt import Behaviour, Status


class StateTask(Behaviour):

    def __init__(self, state):
        super().__init__()
        self.default_state = state

    def initialize(self):
        self.state = self.default_state

    def update(self) -> Status:
        return self.state

    def terminate(self):
        pass


class XThenY(Behaviour):

    def __init__(self, x: Status, y: Status):
        super().__init__()
        self.accessed = False
        self.x, self.y = x, y

    def initialize(self):
        self.state = self.x

    def update(self) -> Status:
        if self.accessed:
            self.state = self.y
        else:
            self.accessed = True
        return self.state

    def terminate(self):
        pass


class SuccessTask(StateTask):
    def __init__(self):
        super().__init__(Status.SUCCESS)


class FailureTask(StateTask):
    def __init__(self):
        super().__init__(Status.FAILURE)


class RunningTask(StateTask):
    def __init__(self):
        super().__init__(Status.RUNNING)

__all__ = [
    "RunningTask",
    "SuccessTask",
    "FailureTask",
    "XThenY",
]
