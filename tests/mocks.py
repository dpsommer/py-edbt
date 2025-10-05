from edbt import Behaviour, Status
from edbt.rules import Condition


class StateTask(Behaviour):

    def __init__(self, state):
        super().__init__()
        self.default_state = state

    def _initialize(self):
        self.state = self.default_state

    def _update(self) -> Status:
        return self.state


class XThenY(Behaviour):

    def __init__(self, x: Status, y: Status):
        super().__init__()
        self.accessed = False
        self.x, self.y = x, y

    def _initialize(self):
        self.state = self.x

    def _update(self) -> Status:
        if self.accessed:
            self.state = self.y
        else:
            self.accessed = True
        return self.state


class SuccessTask(StateTask):
    def __init__(self):
        super().__init__(Status.SUCCESS)


class FailureTask(StateTask):
    def __init__(self):
        super().__init__(Status.FAILURE)


class RunningTask(StateTask):
    def __init__(self):
        super().__init__(Status.RUNNING)


class AlwaysTrue(Condition):
    def __call__(self, *args, **kwargs):
        return True
