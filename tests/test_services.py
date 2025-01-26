import asyncio
import time

import pytest

from edbt import (
    BehaviourTree,
    CheckMailbox,
    Message,
    RequestHandler,
    Selector,
    Status,
)

from .mocks import AlwaysTrue, SuccessTask, RunningTask

TEST_KEY = "test"
CHECK_MAILBOX_FREQUENCY = 0.1


@pytest.fixture
def rh_selector(tree):
    selector = Selector(tree)
    rh = RequestHandler(tree, selector, TEST_KEY, SuccessTask())
    selector.add_child(rh)
    selector.add_child(RunningTask())
    return selector


@pytest.fixture
def mailbox(tree: BehaviourTree, rh_selector):
    return CheckMailbox(tree, rh_selector, CHECK_MAILBOX_FREQUENCY)


async def test_check_mailbox(tree: BehaviourTree, mailbox: CheckMailbox):
    tree.root = mailbox

    msg = Message(
        sender=None,
        request=(TEST_KEY, ()),
        condition=AlwaysTrue,
        timeout=time.time_ns() + (2 * 1_000_000_000)
    )

    tree.tick()

    tree.send_message(msg)
    await asyncio.sleep(0.2)

    tree.tick()

    assert mailbox.state == Status.SUCCESS
