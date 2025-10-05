from typing import List, Type

import pytest

from edbt import Behaviour, BehaviourTree, Status
from edbt.nodes.composite import (
    Composite,
    Parallel,
    Selector,
    Sequencer,
    SuccessPolicy,
)

from . import mocks


def setup_composite(cls: Type[Composite], children: List[Behaviour], *args):
    composite = cls(*args)

    for child in children:
        composite.add_child(child)

    tree = BehaviourTree(composite)
    return tree


@pytest.mark.parametrize(
    "children,expected_states",
    [
        (
            [mocks.FailureTask(), mocks.SuccessTask()],
            [Status.SUCCESS],
        ),
        (
            [mocks.FailureTask(), mocks.RunningTask()],
            [Status.RUNNING],
        ),
        (
            [mocks.FailureTask(), mocks.XThenY(Status.RUNNING, Status.SUCCESS)],
            [Status.RUNNING, Status.SUCCESS],
        ),
    ],
)
def test_selector(children, expected_states):
    tree = setup_composite(Selector, children)

    for state in expected_states:
        assert tree.tick() == state


@pytest.mark.parametrize(
    "children,expected_states",
    [
        (
            [mocks.XThenY(Status.SUCCESS, Status.FAILURE)],
            [Status.SUCCESS, Status.FAILURE],
        ),
        (
            [mocks.SuccessTask(), mocks.RunningTask()],
            [Status.RUNNING],
        ),
        (
            [mocks.SuccessTask(), mocks.XThenY(Status.RUNNING, Status.SUCCESS)],
            [Status.RUNNING, Status.SUCCESS],
        ),
    ],
)
def test_sequencer(children, expected_states):
    tree = setup_composite(Sequencer, children)

    for state in expected_states:
        assert tree.tick() == state


@pytest.mark.parametrize(
    "policy,children,expected_states",
    [
        (
            SuccessPolicy.REQUIRE_ONE,
            [mocks.FailureTask(), mocks.SuccessTask()],
            [Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [mocks.FailureTask(), mocks.FailureTask()],
            [Status.FAILURE],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [mocks.SuccessTask(), mocks.SuccessTask()],
            [Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [mocks.SuccessTask(), mocks.SuccessTask(), mocks.FailureTask()],
            [Status.FAILURE],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [mocks.FailureTask(), mocks.FailureTask(), mocks.RunningTask()],
            [Status.RUNNING],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [mocks.RunningTask(), mocks.SuccessTask(), mocks.FailureTask()],
            [Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [mocks.RunningTask(), mocks.SuccessTask(), mocks.FailureTask()],
            [Status.FAILURE],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [
                mocks.FailureTask(),
                mocks.XThenY(Status.RUNNING, Status.SUCCESS),
                mocks.FailureTask(),
            ],
            [Status.RUNNING, Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [
                mocks.SuccessTask(),
                mocks.XThenY(Status.RUNNING, Status.FAILURE),
                mocks.SuccessTask(),
            ],
            [Status.RUNNING, Status.FAILURE],
        ),
    ],
)
def test_parallel(policy, children, expected_states):
    tree = setup_composite(Parallel, children, policy)

    for state in expected_states:
        assert tree.tick() == state
