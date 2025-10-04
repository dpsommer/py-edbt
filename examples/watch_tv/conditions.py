import edbt
from edbt import blackboard

from common import *


class IsOnCouch(edbt.Condition):
    def _initialize(self):
        if COUCH_SEATS_KEY not in blackboard.get_blackboard():
            blackboard.write(COUCH_SEATS_KEY, [])

    def __call__(self, *args, **kwargs):
        return len(blackboard.read(COUCH_SEATS_KEY)) > 0


class IsDrinkEmpty(edbt.Condition):
    def __call__(self, *args, **kwargs):
        held_object = blackboard.read(HELD_OBJECT_KEY, AGENT_NAMESPACE)
        return type(held_object) is not Drink or held_object.sips_remaining == 0
