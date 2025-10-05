# trunk-ignore-all(black)
import pytest

from edbt import blackboard
from edbt.builder import TreeBuilder, TreeBuilderException
from edbt.rules import HasValue, IsEqual, LowerPriority

from . import mocks

TEST_KEY = "test"
TEST_VALUE = "test"


def test_builder():
    tree = (
        TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .leaf(mocks.SuccessTask())
                .leaf(mocks.RunningTask())
            .build()
    )
    assert tree.tick() == mocks.Status.RUNNING


def test_nested_composites():
    tree = (
        TreeBuilder()
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
        TreeBuilder()
            .selector()
                .request_handler(TEST_KEY)
                    .selector()
                        .leaf(mocks.FailureTask())
                        .leaf(HasValue(TEST_KEY))
                        .done()
                    .leaf(mocks.RunningTask())
            .build()
    )

    blackboard.write(TEST_KEY, TEST_VALUE)
    assert tree.tick() == mocks.Status.SUCCESS


def test_failed_insert():
    with pytest.raises(TreeBuilderException):
        (
            TreeBuilder()
                .selector()
                    .leaf(mocks.FailureTask())
                    .leaf(mocks.SuccessTask())
                    .done()
                .leaf(mocks.RunningTask())
                .build()
        )


def test_done_without_composite():
    with pytest.raises(TreeBuilderException):
        (
            TreeBuilder()
                .selector()
                    .leaf(mocks.FailureTask())
                    .leaf(mocks.SuccessTask())
                    .done()
                .done()
                .build()
        )


def test_bod_without_composite():
    with pytest.raises(TreeBuilderException):
        (
            TreeBuilder()
                .blackboard_observer(
                    key=TEST_KEY,
                    condition=IsEqual(TEST_KEY, TEST_VALUE),
                    abort_rule=LowerPriority,
                )
                    .leaf(mocks.SuccessTask())
                .build()
        )


def test_request_handler_without_composite():
    with pytest.raises(TreeBuilderException):
        (
            TreeBuilder()
                .request_handler(TEST_KEY)
                    .leaf(mocks.SuccessTask())
                .build()
        )


def test_empty_decorator_raises():
    with pytest.raises(TreeBuilderException):
        (
            TreeBuilder()
                .selector()
                    .leaf(mocks.FailureTask())
                .request_handler(TEST_KEY)
            .build()
        )
