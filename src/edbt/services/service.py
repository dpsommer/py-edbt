import asyncio
from abc import abstractmethod

import edbt

background_tasks = set()


class Service(edbt.Behaviour):
    def __init__(self, child: edbt.Behaviour, frequency: float):
        super().__init__()
        self.child = child
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
        self.state = edbt.Status.RUNNING
        if not self._running:
            # run the service as a background coroutine
            task = asyncio.create_task(self.service())
            # keep a reference to the task to avoid it being GC'd;
            # discard it on completion after it's stopped
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            self._running = True

    def _update(self):
        return self.child.tick()

    def _terminate(self):
        self._running = False

    def abort(self):
        super().abort()
        self._terminate()
        self.child.abort()
