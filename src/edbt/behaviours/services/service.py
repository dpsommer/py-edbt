import asyncio
from abc import abstractmethod

from edbt import (
    Behaviour,
    Status,
    BehaviourTree,
)

_background_tasks = set()


class Service(Behaviour):
    def __init__(self, tree: BehaviourTree, child: Behaviour, frequency: float):
        super().__init__()
        self.child = child
        self._tree = tree
        self._active = True
        self._running = False
        self._frequency = frequency

    def reset(self):
        super().reset()
        self.child.reset()

    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False

    async def service(self):
        while self._running:
            if not self._active:
                await asyncio.sleep(self._frequency)
                continue
            await self._run()
            await asyncio.sleep(self._frequency)

    @abstractmethod
    async def _run(self):
        pass

    def _initialize(self):
        self.state = Status.RUNNING
        if not self._running:
            # run the service as a background coroutine
            task = asyncio.create_task(self.service())
            # keep a reference to the task to avoid it being GC'd;
            # discard it on completion after it's stopped
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)
            self._running = True
        self._tree.start(self.child, self._on_child_complete)

    def _update(self):
        return self.state

    def _terminate(self):
        self._running = False

    def _abort(self):
        super()._abort()
        self._terminate()
        self._tree.abort(self.child)

    def _on_child_complete(self, status: Status) -> None:
        if status is Status.SUCCESS:
            self.state = status
        else:
            self.state = Status.FAILURE
        self._terminate()
