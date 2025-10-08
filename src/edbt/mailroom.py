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
    expiry: int


class MailRoom:
    """Global controller for messages sent between agents

    Messages are pushed to a minheap priority queue based on their defined
    expiry time. Each cycle, messages are popped from the
    """

    def __init__(self):
        self._mailbox: List[Tuple[int, Message]] = []
        self._running = True

    def send_message(self, msg: Message):
        heappush(self._mailbox, (msg.expiry, msg))

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
            pending_messages = self._check_mail()
            # when we run out of messages, push any pending messages back into
            # the queue and sleep until the next cycle
            for msg in pending_messages:
                self.send_message(msg)
            await asyncio.sleep(MAIL_ROOM_CHECK_FREQUENCY)

    def _check_mail(self) -> List[Message]:
        pending_messages = []
        while self._mailbox:
            expiry, msg = heappop(self._mailbox)
            is_expired = expiry <= time.time_ns()

            if is_expired:
                continue

            # we still want to evaluate messages that don't meet the defined
            # condition, so keep them to be pushed back into the queue
            if not msg.condition():
                pending_messages.append(msg)
            else:
                k, v = msg.request
                blackboard.write(k, v, msg.receiver)
        return pending_messages


mail_room = MailRoom()

__all__ = ["Message", "MAIL_ROOM_CHECK_FREQUENCY", "mail_room"]
