import pytest

import edbt
from edbt import builder
from edbt import blackboard

from .mocks import *

TEST_KEY = "test"
TEST_VALUE = "test"


def test_builder():
    tree = (builder.TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .leaf(SuccessTask())
                .leaf(RunningTask())
            .build())
    assert tree.tick() == Status.RUNNING


def test_nested_composites():
    tree = (builder.TreeBuilder()
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
    tree = (builder.TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .selector()
                        .leaf(FailureTask())
                        .leaf(edbt.HasValue(TEST_KEY))
                        .done()
                .leaf(RunningTask())
            .build())

    blackboard.write(TEST_KEY, TEST_VALUE)
    assert tree.tick() == Status.SUCCESS


def test_failed_insert():
    with pytest.raises(builder.TreeBuilderException):
        (builder.TreeBuilder()
            .selector()
                .leaf(FailureTask())
                .leaf(SuccessTask())
            .done()
            .leaf(RunningTask())
            .build())


def test_done_without_composite():
    with pytest.raises(builder.TreeBuilderException):
        (builder.TreeBuilder()
            .selector()
                .leaf(FailureTask())
                .leaf(SuccessTask())
            .done()
            .done()
            .build())


def test_bod_without_composite():
    with pytest.raises(builder.TreeBuilderException):
        (builder.TreeBuilder()
            .blackboard_observer(
                key=TEST_KEY,
                condition=edbt.IsEqual(TEST_KEY, TEST_VALUE),
                abort_rule=edbt.LowerPriority)
                .leaf(SuccessTask())
            .build())


def test_request_handler_without_composite():
    with pytest.raises(builder.TreeBuilderException):
        (builder.TreeBuilder()
            .request_handler(TEST_KEY)
                .leaf(SuccessTask())
            .build())


def test_empty_decorator_raises():
    with pytest.raises(builder.TreeBuilderException):
        (builder.TreeBuilder()
            .selector()
                .leaf(FailureTask())
                .request_handler(TEST_KEY)
            .build())
