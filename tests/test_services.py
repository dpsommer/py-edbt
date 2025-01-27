import asyncio
import time

import pytest

from edbt import (
    mailroom,
    BehaviourTree,
    Message,
    RequestHandler,
    Selector,
    Status,
)

from .mocks import AlwaysTrue, SuccessTask, RunningTask

TEST_KEY = "test"
CHECK_MAILBOX_FREQUENCY = 0.1


@pytest.fixture
def rh_selector():
    selector = Selector()
    selector.add_child(RequestHandler(
        key=TEST_KEY,
        parent=selector,
        child=SuccessTask()
    ))
    selector.add_child(RunningTask())
    return selector


@pytest.fixture(autouse=True)
async def open_mailroom():
    mailroom.start()
    yield mailroom
    mailroom.stop()


async def test_check_mailbox(rh_selector: Selector):
    tree = BehaviourTree(rh_selector)

    tree.tick()

    mailroom.send_message(Message(
        sender=None,
        receiver=tree,
        request=(TEST_KEY, ()),
        condition=AlwaysTrue,
        timeout=time.time_ns() + (2 * 1_000_000_000)
    ))
    await asyncio.sleep(0.2)

    tree.tick()

    assert rh_selector.state == Status.SUCCESS
