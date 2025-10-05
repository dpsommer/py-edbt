import pytest

from edbt import BehaviourTree, blackboard
from edbt.composite import Selector
from edbt.conditions import HasValue, IsEqual
from edbt.decorators import BOD, LowerPriority

from . import mocks

TEST_KEY = "test"
TEST_VALUE = "test"


def setup_bod(parent, condition, abort_rule=None):
    bod = BOD(
        child=mocks.SuccessTask(),
        key=TEST_KEY,
        condition=condition,
        abort_rule=abort_rule,
    )
    parent.add_child(bod)
    parent.add_child(mocks.RunningTask())

    return bod


@pytest.mark.parametrize(
    "condition,state,expected",
    (
        [HasValue(TEST_KEY), dict(), mocks.Status.FAILURE],
        [HasValue(TEST_KEY), {TEST_KEY: TEST_VALUE}, mocks.Status.SUCCESS],
        [
            IsEqual(TEST_KEY, TEST_VALUE),
            {TEST_KEY: "wrong_value"},
            mocks.Status.FAILURE,
        ],
        [
            IsEqual(TEST_KEY, TEST_VALUE),
            {TEST_KEY: TEST_VALUE},
            mocks.Status.SUCCESS,
        ],
    ),
)
def test_bod_conditions(
    condition: mocks.Condition, state: dict, expected: mocks.Status
):
    parent = Selector()
    tree = BehaviourTree(parent)
    bod = setup_bod(parent, condition)
    for k, v in state.items():
        blackboard.write(k, v)
    tree.tick()

    assert bod.state == expected


def test_lower_priority_abort_rule():
    parent = Selector()
    tree = BehaviourTree(parent)
    setup_bod(parent, HasValue(TEST_KEY), LowerPriority(parent))
    tree.tick()  # initialize the bod and its observer
    blackboard.write(TEST_KEY, TEST_VALUE)
    tree.tick()

    assert parent._children[1].state == mocks.Status.ABORTED
