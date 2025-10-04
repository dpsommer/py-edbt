import common

import edbt
from edbt import blackboard


class IsOnCouch(edbt.Condition):
    def _initialize(self):
        if common.COUCH_SEATS_KEY not in blackboard.get_blackboard():
            blackboard.write(common.COUCH_SEATS_KEY, [])

    def __call__(self, *args, **kwargs):
        return len(blackboard.read(common.COUCH_SEATS_KEY)) > 0


class IsDrinkEmpty(edbt.Condition):
    def __call__(self, *args, **kwargs):
        held_object = blackboard.read(common.HELD_OBJECT_KEY, common.AGENT_NAMESPACE)
        return type(held_object) is not common.Drink or held_object.sips_remaining == 0
