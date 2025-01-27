from dataclasses import dataclass
from heapq import heappush, heappop
from typing import Callable, Tuple

from .behaviour import Behaviour
from .status import Status


@dataclass
class Message:
    sender: "BehaviourTree"
    request: Tuple[str, tuple]
    condition: Callable[[], bool]
    timeout: int


class BehaviourTree:

    def __init__(self, root: Behaviour):
        self.root = root
        self._mailbox = []

    def tick(self) -> Status:
        return self.root.tick()

    def send_message(self, msg: Message, priority: int=None):
        heappush(self._mailbox, (priority or msg.timeout, msg))

    def read_message(self) -> Tuple[int, Message]:
        return heappop(self._mailbox)

    def mailbox_size(self) -> int:
        return len(self._mailbox)
