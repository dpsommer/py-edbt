import mocks
import pytest

import edbt
from edbt import blackboard

TEST_KEY = "test"
TEST_VALUE = "test"


def setup_bod(parent, condition, abort_rule=None):
    bod = edbt.BOD(
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
        [edbt.HasValue(TEST_KEY), dict(), mocks.Status.FAILURE],
        [edbt.HasValue(TEST_KEY), {TEST_KEY: TEST_VALUE}, mocks.Status.SUCCESS],
        [
            edbt.IsEqual(TEST_KEY, TEST_VALUE),
            {TEST_KEY: "wrong_value"},
            mocks.Status.FAILURE,
        ],
        [
            edbt.IsEqual(TEST_KEY, TEST_VALUE),
            {TEST_KEY: TEST_VALUE},
            mocks.Status.SUCCESS,
        ],
    ),
)
def test_bod_conditions(
    condition: mocks.Condition, state: dict, expected: mocks.Status
):
    parent = edbt.Selector()
    tree = edbt.BehaviourTree(parent)
    bod = setup_bod(parent, condition)
    for k, v in state.items():
        blackboard.write(k, v)
    tree.tick()

    assert bod.state == expected


def test_lower_priority_abort_rule():
    parent = edbt.Selector()
    tree = edbt.BehaviourTree(parent)
    setup_bod(parent, edbt.HasValue(TEST_KEY), edbt.LowerPriority(parent))
    tree.tick()  # initialize the bod and its observer
    blackboard.write(TEST_KEY, TEST_VALUE)
    tree.tick()

    assert parent._children[1].state == mocks.Status.ABORTED
