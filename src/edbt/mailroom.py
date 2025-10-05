import asyncio
import time
from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Callable, List, Tuple

from edbt import background_tasks, blackboard

MAIL_ROOM_CHECK_FREQUENCY = 0.1


@dataclass
class Message:
    # blackboard namespaces for sender/receiver
    sender: str
    receiver: str
    request: Tuple[str, tuple]
    condition: Callable[[], bool]
    timeout: int


class MailRoom:
    def __init__(self):
        self._mailbox: List[Tuple[int, Message]] = []
        self._running = True

    def send_message(self, msg: Message, priority: int = None):
        heappush(self._mailbox, (priority or msg.timeout, msg))

    def start(self):
        task = asyncio.create_task(self._run())
        # keep a reference to the task to avoid it being GC'd;
        # discard it on completion after it's stopped
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    def stop(self):
        self._running = False

    async def _run(self):
        while self._running:
            try:
                # FIXME: mail sent with priority isn't read
                timeout, msg = heappop(self._mailbox)
                now = time.time_ns()
                if timeout > now and msg.condition():
                    k, v = msg.request
                    blackboard.write(k, v, msg.receiver)
            # when we run out of messages, sleep til next cycle
            except IndexError:
                await asyncio.sleep(MAIL_ROOM_CHECK_FREQUENCY)


mail_room = MailRoom()

__all__ = ["Message", "mail_room"]
