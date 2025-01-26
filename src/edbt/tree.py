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


class BehaviourTree:

    root: Behaviour

    def __init__(self):
        self.root = None
        self.values = dict()
        self.observers = defaultdict(set)
        self._scheduler: deque[Behaviour] = deque()
        self._mailbox = []

    def tick(self) -> Status:
        if len(self._scheduler) == 0:
            self.start(self.root)
            if self.root.state != Status.INVALID:
                self.root.reset()
        # use None to mark the end of each tick
        self._scheduler.append(None)
        while self.step():
            continue
        return self.root.state

    def step(self) -> bool:
        b = self._scheduler.popleft()
        if b is None:
            return False

        state = b.tick()
        if state == Status.RUNNING:
            self._scheduler.append(b)
        elif b.observer is not None:
            b.observer(state)

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
        try:
            behaviour._abort()
            if behaviour.observer is not None:
                behaviour.observer(Status.ABORTED)
            self._scheduler.remove(behaviour)
        except ValueError:
            pass  # noop if the behaviour isn't scheduled

    def update_blackboard(self, k: str, v):
        self.values[k] = v
        # trigger any observer callbacks
        if k in self.observers:
            # make a copy of the observer set here with list
            # as the callback may modify the set
            for o in list(self.observers[k]):
                if o is not None:
                    o(v)

    def add_observer(self, key: str, obs: BlackboardObserver):
        self.observers[key].add(obs)

    def remove_observer(self, key: str, obs: BlackboardObserver):
        try:
            self.observers[key].remove(obs)
        except KeyError:
            pass  # noop if key or obs aren't in the map

    def send_message(self, msg: Message, priority: int=None):
        heappush(self._mailbox, (priority or msg.timeout, msg))

    def read_message(self) -> Tuple[int, Message]:
        return heappop(self._mailbox)

    def mailbox_size(self) -> int:
        return len(self._mailbox)
