# trunk-ignore-all(black)
import mocks
import pytest

import edbt
from edbt import blackboard, builder

TEST_KEY = "test"
TEST_VALUE = "test"


def test_builder():
    tree = (
        builder.TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .leaf(mocks.SuccessTask())
                .leaf(mocks.RunningTask())
            .build()
    )
    assert tree.tick() == mocks.Status.RUNNING


def test_nested_composites():
    tree = (
        builder.TreeBuilder()
            .selector()
                .leaf(mocks.FailureTask())
                .sequencer()
                    .leaf(mocks.SuccessTask())
                    .leaf(mocks.SuccessTask())
                    .done()
                .leaf(mocks.FailureTask())
            .build()
    )
    assert tree.tick() == mocks.Status.SUCCESS


def test_composite_decorator_child():
    tree = (
        builder.TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .selector()
                        .leaf(mocks.FailureTask())
                        .leaf(edbt.HasValue(TEST_KEY))
                        .done()
                    .leaf(mocks.RunningTask())
            .build()
    )

    blackboard.write(TEST_KEY, TEST_VALUE)
    assert tree.tick() == mocks.Status.SUCCESS


def test_failed_insert():
    with pytest.raises(builder.TreeBuilderException):
        (
            builder.TreeBuilder()
                .selector()
                    .leaf(mocks.FailureTask())
                    .leaf(mocks.SuccessTask())
                    .done()
                .leaf(mocks.RunningTask())
                .build()
        )


def test_done_without_composite():
    with pytest.raises(builder.TreeBuilderException):
        (
            builder.TreeBuilder()
                .selector()
                    .leaf(mocks.FailureTask())
                    .leaf(mocks.SuccessTask())
                    .done()
                .done()
                .build()
        )


def test_bod_without_composite():
    with pytest.raises(builder.TreeBuilderException):
        (
            builder.TreeBuilder()
                .blackboard_observer(
                    key=TEST_KEY,
                    condition=edbt.IsEqual(TEST_KEY, TEST_VALUE),
                    abort_rule=edbt.LowerPriority,
                )
                    .leaf(mocks.SuccessTask())
                .build()
        )


def test_request_handler_without_composite():
    with pytest.raises(builder.TreeBuilderException):
        (
            builder.TreeBuilder()
                .request_handler(TEST_KEY)
                    .leaf(mocks.SuccessTask())
                .build()
        )


def test_empty_decorator_raises():
    with pytest.raises(builder.TreeBuilderException):
        (
            builder.TreeBuilder()
                .selector()
                    .leaf(mocks.FailureTask())
                .request_handler(TEST_KEY)
            .build()
        )
