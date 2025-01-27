from edbt import blackboard, Status
from edbt.builder import TreeBuilder

from .mocks import *

TEST_KEY = "test"


def test_builder():
    tree = (TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .leaf(SuccessTask())
                .leaf(RunningTask())
            .build())
    assert tree.tick() == Status.RUNNING


def test_nested_composites():
    tree = (TreeBuilder()
            .selector()
                .leaf(FailureTask())
                .sequencer()
                    .leaf(SuccessTask())
                    .leaf(SuccessTask())
                .done()
                .leaf(FailureTask())
            .build())
    assert tree.tick() == Status.SUCCESS


def test_composite_decorator_child():
    tree = (TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .selector()
                        .leaf(FailureTask())
                        .leaf(SuccessTask())
                    .done()
                .leaf(RunningTask())
            .build())

    blackboard[TEST_KEY] = "test"
    assert tree.tick() == Status.SUCCESS
