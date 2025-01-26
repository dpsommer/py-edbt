from typing import List, Type
import pytest

from edbt import (
    BehaviourTree,
    Behaviour,
    Composite,
    Parallel,
    SuccessPolicy,
    Selector,
    Sequencer,
    Status,
)

from .mocks import *


def setup_composite(tree: BehaviourTree, cls: Type[Composite], children: List[Behaviour], *args):
    composite = cls(tree, *args)

    for child in children:
        composite.add_child(child)

    tree.root = composite
    return composite


@pytest.mark.parametrize(
    "children,expected_states", [
        (
            [FailureTask(), SuccessTask()],
            [Status.SUCCESS],
        ),
        (
            [FailureTask(), RunningTask()],
            [Status.RUNNING],
        ),
        (
            [FailureTask(), XThenY(Status.RUNNING, Status.SUCCESS)],
            [Status.RUNNING, Status.SUCCESS],
        ),
    ]
)
def test_selector(tree, children, expected_states):
    selector = setup_composite(tree, Selector, children)

    for state in expected_states:
        tree.tick()
        assert selector.state == state


@pytest.mark.parametrize(
    "children,expected_states", [
        (
            [XThenY(Status.SUCCESS, Status.FAILURE)],
            [Status.SUCCESS, Status.SUCCESS, Status.FAILURE],
        ),
        (
            [SuccessTask(), RunningTask()],
            [Status.RUNNING],
        ),
        (
            [SuccessTask(), XThenY(Status.RUNNING, Status.SUCCESS)],
            [Status.RUNNING, Status.SUCCESS],
        ),
    ]
)
def test_sequencer(tree, children, expected_states):
    sequencer = setup_composite(tree, Sequencer, children)

    for state in expected_states:
        tree.tick()
        assert sequencer.state == state


@pytest.mark.parametrize(
    "policy,children,expected_states", [
        (
            SuccessPolicy.REQUIRE_ONE,
            [FailureTask(), SuccessTask()],
            [Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [FailureTask(), FailureTask()],
            [Status.FAILURE],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [SuccessTask(), SuccessTask()],
            [Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [SuccessTask(), SuccessTask(), FailureTask()],
            [Status.FAILURE],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [FailureTask(), FailureTask(), RunningTask()],
            [Status.RUNNING],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [RunningTask(), SuccessTask(), FailureTask()],
            [Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [RunningTask(), SuccessTask(), FailureTask()],
            [Status.FAILURE],
        ),
        (
            SuccessPolicy.REQUIRE_ONE,
            [FailureTask(), XThenY(Status.RUNNING, Status.SUCCESS), FailureTask()],
            [Status.RUNNING, Status.SUCCESS],
        ),
        (
            SuccessPolicy.REQUIRE_ALL,
            [SuccessTask(), XThenY(Status.RUNNING, Status.FAILURE), SuccessTask()],
            [Status.RUNNING, Status.FAILURE],
        ),
    ]
)
def test_parallel(tree, policy, children, expected_states):
    parallel = setup_composite(tree, Parallel, children, policy)


    for state in expected_states:
        tree.tick()
        assert parallel.state == state
