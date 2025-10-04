# trunk-ignore-all(black)
import asyncio

import actions
import common
import conditions

import edbt
from edbt.builder import TreeBuilder


async def main():
    default_blackboard = edbt.blackboard.get_blackboard()
    default_blackboard[common.COUCH_OCCUPANCY_KEY] = 2
    default_blackboard[common.DRINKS_COUNT_KEY] = 5

    agent_blackboard = edbt.blackboard.get_blackboard(common.AGENT_NAMESPACE)

    get_drink_from_fridge = (
        TreeBuilder()
            .sequencer()
                .selector()
                    .inverse().leaf(conditions.IsOnCouch())
                    .leaf(actions.GetUpFromCouch())
                    .done()
                .leaf(actions.OpenFridge())
                .selector()
                    .leaf(actions.GrabDrink())
                    .leaf(actions.CloseFridge())
                    .done()
                .leaf(actions.CloseFridge())
        .build()
    )

    watch_tv = (
        TreeBuilder()
            .selector()
                .blackboard_observer(
                    key=common.IS_THIRSTY_KEY,
                    namespace=common.AGENT_NAMESPACE,
                    condition=edbt.IsEqual(common.IS_THIRSTY_KEY, True, common.AGENT_NAMESPACE),
                    abort_rule=edbt.LowerPriority,
                )
                    .sequencer()
                        .selector()
                            .inverse().leaf(conditions.IsDrinkEmpty())
                            .add_subtree(get_drink_from_fridge)
                            .done()
                        .selector()
                            .leaf(conditions.IsOnCouch())
                            .leaf(actions.SitOnCouch())
                            .done()
                        .leaf(actions.SipDrink())
                        .done()
                .leaf(actions.WatchTV())
            .build()
    )

    watch_the_game = (
        TreeBuilder()
            .sequencer()
                .selector()
                    .leaf(conditions.IsOnCouch())
                    .leaf(actions.SitOnCouch())
                    .done()
                .add_subtree(watch_tv)
            .build()
    )

    for _ in range(30):
        print(watch_the_game.tick())
        print([f"{k}: {v}" for k, v in default_blackboard.items()])
        print([f"{k}: {v}" for k, v in agent_blackboard.items()])
        drink = agent_blackboard.get(common.HELD_OBJECT_KEY)
        if type(drink) is common.Drink:
            print(drink.sips_remaining)
        print()


asyncio.run(main())
