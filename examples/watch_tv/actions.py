import common

import edbt
from edbt import blackboard


class OpenFridge(edbt.Behaviour):
    def _update(self):
        blackboard.write(common.FRIDGE_OPEN_KEY, True)
        return edbt.Status.SUCCESS


class GrabDrink(edbt.Behaviour):
    def _update(self):
        if blackboard.read(common.FRIDGE_OPEN_KEY) and blackboard.read(
            common.DRINKS_COUNT_KEY
        ):
            drinks_count = blackboard.read(common.DRINKS_COUNT_KEY)
            blackboard.write(common.DRINKS_COUNT_KEY, drinks_count - 1)
            # read containing tree from async context
            blackboard.write(
                common.HELD_OBJECT_KEY, common.Drink(), common.AGENT_NAMESPACE
            )
            return edbt.Status.SUCCESS
        return edbt.Status.FAILURE


class CloseFridge(edbt.Behaviour):
    def _initialize(self):
        if common.FRIDGE_OPEN_KEY not in blackboard.get_blackboard():
            blackboard.write(common.FRIDGE_OPEN_KEY, False)

    def _update(self):
        blackboard.write(common.FRIDGE_OPEN_KEY, False)
        return edbt.Status.SUCCESS


class SitOnCouch(edbt.Behaviour):
    def _initialize(self):
        if common.COUCH_SEATS_KEY not in blackboard.get_blackboard():
            blackboard.write(common.COUCH_SEATS_KEY, [])

    def _update(self):
        couch_seats = blackboard.read(common.COUCH_SEATS_KEY)
        if len(couch_seats) >= blackboard.read(common.COUCH_OCCUPANCY_KEY):
            return edbt.Status.FAILURE
        # XXX: how can we pass a reference to the containing tree in a nice way?
        couch_seats.append("placeholder")
        return edbt.Status.SUCCESS


class GetUpFromCouch(edbt.Behaviour):
    def _initialize(self):
        if common.COUCH_SEATS_KEY not in blackboard.get_blackboard():
            blackboard.write(common.COUCH_SEATS_KEY, [])

    def _update(self):
        couch_seats = blackboard.read(common.COUCH_SEATS_KEY)
        if len(couch_seats) == 0:
            return edbt.Status.FAILURE
        # FIXME: use a UUID here (for behaviour or tree?)
        couch_seats.pop()
        return edbt.Status.SUCCESS


class SipDrink(edbt.Behaviour):
    def _update(self):
        held_object = blackboard.read(common.HELD_OBJECT_KEY, common.AGENT_NAMESPACE)
        if type(held_object) is not common.Drink:
            return edbt.Status.FAILURE

        try:
            held_object.take_sip()
            blackboard.write(
                key=common.IS_THIRSTY_KEY,
                value=False,
                namespace=common.AGENT_NAMESPACE,
            )
            return edbt.Status.SUCCESS
        except ValueError:
            return edbt.Status.FAILURE


class WatchTV(edbt.Behaviour):
    def __init__(self):
        super().__init__()
        self._time_spent = 0

    def _initialize(self):
        self.state = edbt.Status.RUNNING

    def _update(self):
        self._time_spent += 1
        print("watching TV for", self._time_spent)
        if self._time_spent % 3 == 0:
            blackboard.write(
                key=common.IS_THIRSTY_KEY,
                value=True,
                namespace=common.AGENT_NAMESPACE,
            )
        return self.state
