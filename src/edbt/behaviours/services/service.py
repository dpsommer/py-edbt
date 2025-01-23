import time
from abc import abstractmethod
from multiprocessing import Process

from edbt import (
    Behaviour,
    Status,
    BehaviourTree,
)


class Service(Behaviour):
    def __init__(self, tree: BehaviourTree, child: Behaviour, frequency: float):
        super().__init__()
        self.child = child
        self._tree = tree
        self._active = True
        self._stopped = True
        self._frequency = frequency
        self._proc = Process(target=self.service)

    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False

    def service(self):
        while not self._stopped:
            if not self._active:
                time.sleep(self._frequency)
            self._run()
            time.sleep(self._frequency)

    @abstractmethod
    def _run(self):
        pass

    def _initialize(self):
        if self._stopped:
            self._stopped = False
            self._proc.start()
        self._tree.start(self.child, self._on_child_complete)

    def _update(self):
        return Status.RUNNING

    def _terminate(self):
        self._stopped = True
        self._proc.join()

    def _abort(self):
        self.state = Status.ABORTED
        self._terminate()
        self._tree.abort(self.child)

    def _on_child_complete(self, status: Status) -> None:
        if status is Status.SUCCESS:
            self.state = status
        else:
            self.state = Status.FAILURE
        self._terminate()
