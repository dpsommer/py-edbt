import asyncio

import edbt
from edbt.builder import TreeBuilder

from common import *
from actions import *
from conditions import *


async def main():
    default_blackboard = edbt.blackboard.get_blackboard()
    default_blackboard[COUCH_OCCUPANCY_KEY] = 2
    default_blackboard[DRINKS_COUNT_KEY] = 5

    agent_blackboard = edbt.blackboard.get_blackboard(AGENT_NAMESPACE)

    get_drink_from_fridge = (
        TreeBuilder()
            .sequencer()
                .selector()
                    .inverse().leaf(IsOnCouch())
                    .leaf(GetUpFromCouch())
                    .done()
                .leaf(OpenFridge())
                .selector()
                    .leaf(GrabDrink())
                    .leaf(CloseFridge())
                    .done()
                .leaf(CloseFridge())
            .build())

    watch_tv = (
        TreeBuilder()
            .selector()
                .blackboard_observer(
                        key=IS_THIRSTY_KEY,
                        namespace=AGENT_NAMESPACE,
                        condition=edbt.IsEqual(IS_THIRSTY_KEY, True, AGENT_NAMESPACE),
                        abort_rule=edbt.LowerPriority)
                    .sequencer()
                        .selector()
                            .inverse().leaf(IsDrinkEmpty())
                            .add_subtree(get_drink_from_fridge)
                            .done()
                        .selector()
                            .leaf(IsOnCouch())
                            .leaf(SitOnCouch())
                            .done()
                        .leaf(SipDrink())
                        .done()
                .leaf(WatchTV())
            .build())

    watch_the_game = (
        TreeBuilder()
            .sequencer()
                .selector()
                    .leaf(IsOnCouch())
                    .leaf(SitOnCouch())
                    .done()
                .add_subtree(watch_tv)
            .build())

    for _ in range(30):
        print(watch_the_game.tick())
        print([f"{k}: {v}" for k, v in default_blackboard.items()])
        print([f"{k}: {v}" for k, v in agent_blackboard.items()])
        drink = agent_blackboard.get(HELD_OBJECT_KEY)
        if type(drink) is Drink:
            print(drink.sips_remaining)
        print()

asyncio.run(main())
