import pytest

from edbt import (
    blackboard,
    BehaviourTree,
    BOD,
    Condition,
    Selector,
    Status,
    LowerPriority,
    HasValue,
    IsEqual,
)

from .mocks import *

TEST_KEY = "test"
TEST_VALUE = "test"


def setup_bod(parent, condition, abort_rule=None):
    bod = BOD(
        child=SuccessTask(),
        key=TEST_KEY,
        condition=condition,
        abort_rule=abort_rule,
    )
    parent.add_child(bod)
    parent.add_child(RunningTask())

    return bod


@pytest.mark.parametrize(
        "condition,state,expected",
        (
            [HasValue(TEST_KEY), dict(), Status.FAILURE],
            [HasValue(TEST_KEY), {TEST_KEY: TEST_VALUE}, Status.SUCCESS],
            [IsEqual(TEST_KEY, TEST_VALUE), {TEST_KEY: "wrong_value"}, Status.FAILURE],
            [IsEqual(TEST_KEY, TEST_VALUE), {TEST_KEY: TEST_VALUE}, Status.SUCCESS],
        ),
)
def test_bod_conditions(condition: Condition, state: dict, expected: Status):
    parent = Selector()
    tree = BehaviourTree(parent)
    bod = setup_bod(parent, condition)
    for k, v in state.items():
        blackboard[k] = v
    tree.tick()

    assert bod.state == expected


def test_lower_priority_abort_rule():
    parent = Selector()
    tree = BehaviourTree(parent)
    bod = setup_bod(parent, HasValue(TEST_KEY), LowerPriority(parent))
    tree.tick()  # initialize the bod and its observer
    blackboard[TEST_KEY] = TEST_VALUE
    tree.tick()

    assert parent._children[1].state == Status.ABORTED
