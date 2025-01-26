import pytest

from edbt import (
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


def setup_bod(tree, parent, condition, abort_rule=None):
    bod = BOD(
        tree=tree,
        parent=parent,
        child=SuccessTask(),
        key=TEST_KEY,
        value=TEST_VALUE,
        condition=condition,
        abort_rule=abort_rule,
    )
    parent.add_child(bod)
    parent.add_child(RunningTask())

    tree.root = parent
    return bod


@pytest.mark.parametrize(
        "condition,blackboard,expected",
        (
            [HasValue, dict(), Status.FAILURE],
            [HasValue, {TEST_KEY: TEST_VALUE}, Status.SUCCESS],
            [IsEqual, {TEST_KEY: "wrong_value"}, Status.FAILURE],
            [IsEqual, {TEST_KEY: TEST_VALUE}, Status.SUCCESS],
        ),
)
def test_bod_conditions(tree: BehaviourTree, condition: Condition, blackboard: dict, expected: Status):
    parent = Selector(tree)
    bod = setup_bod(tree, parent, condition)
    for k, v in blackboard.items():
        tree.update_blackboard(k, v)
    tree.tick()

    assert bod.state == expected


def test_lower_priority_abort_rule(tree: BehaviourTree):
    parent = Selector(tree)
    bod = setup_bod(tree, parent, HasValue, LowerPriority)
    tree.tick()  # initialize the bod and its observer
    tree.update_blackboard(TEST_KEY, TEST_VALUE)
    tree.tick()

    assert parent._children[1].state == Status.ABORTED
