from collections import deque, defaultdict
from dataclasses import dataclass
from heapq import heappush, heappop
from typing import Callable, Tuple

from .behaviour import Behaviour
from .observers import BlackboardObserver, StatusObserver
from .status import Status


@dataclass
class Message:
    sender: "BehaviourTree"
    request: Tuple[str, tuple]
    condition: Callable[[], bool]
    timeout: int


class Blackboard:

    def __init__(self):
        self.values = dict()
        self.observers = defaultdict(set)


class BehaviourTree:

    def __init__(self):
        self.blackboard = Blackboard()
        self._scheduler: deque[Behaviour] = deque()
        self._mailbox = []

    def tick(self):
        self._scheduler.append(None)
        while self.step():
            continue

    def step(self) -> bool:
        b = self._scheduler.popleft()
        if b is None:
            return False

        state = b.tick()
        if state != Status.RUNNING and b.observer is not None:
            b.observer(state)
        else:
            self._scheduler.append(b)

        return True

    def start(self, behaviour: Behaviour, observer: StatusObserver=None):
        if behaviour.observer is None:
            behaviour.observer = observer
        self._scheduler.appendleft(behaviour)

    def stop(self, behaviour: Behaviour, status: Status):
        if status is Status.RUNNING:
            raise "can't set RUNNING state for stopped behaviour"

        behaviour.state = status
        if behaviour.observer is not None:
            behaviour.observer(status)

    def abort(self, behaviour: Behaviour):
        behaviour._abort()
        self._scheduler.remove(behaviour)

    def update_blackboard(self, k: str, v):
        self.blackboard.values[k] = v
        # trigger any observer callbacks
        if k in self.blackboard.observers:
            # make a copy of the observer set here with list
            # as the callback may modify the set
            for o in list(self.blackboard.observers[k]):
                if o is not None:
                    o(v)

    def add_observer(self, key: str, obs: BlackboardObserver):
        self.blackboard.observers[key].add(obs)

    def remove_observer(self, key: str, obs: BlackboardObserver):
        try:
            self.blackboard.observers[key].remove(obs)
        except KeyError:
            pass  # no-op if key or obs aren't in the map

    def receive_message(self, msg: Message):
        heappush(self._mailbox, (msg.timeout, msg))

    def read_message(self) -> Tuple[int, Message]:
        heappop(self._mailbox)

    def mailbox_size(self) -> int:
        return len(self._mailbox)
