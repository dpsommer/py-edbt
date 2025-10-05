import asyncio
import time

import pytest

from edbt import BehaviourTree, Status
from edbt.mailroom import Message, mail_room
from edbt.nodes import RequestHandler, Selector

from .mocks import AlwaysTrue, RunningTask, SuccessTask

_TEST_KEY = "test"
_NAMESPACE = "test_services"


@pytest.fixture
def rh_selector():
    selector = Selector()
    selector.add_child(
        RequestHandler(
            key=_TEST_KEY, namespace=_NAMESPACE, parent=selector, child=SuccessTask()
        )
    )
    selector.add_child(RunningTask())
    return selector


@pytest.fixture(autouse=True)
async def open_mailroom():
    mail_room.start()
    yield mail_room
    mail_room.stop()


async def test_check_mailbox(rh_selector: Selector):
    tree = BehaviourTree(rh_selector)

    tree.tick()

    mail_room.send_message(
        Message(
            sender=None,
            receiver=_NAMESPACE,
            request=(_TEST_KEY, ()),
            condition=AlwaysTrue,
            timeout=time.time_ns() + (2 * 1_000_000_000),
        )
    )
    await asyncio.sleep(0.2)

    tree.tick()

    assert rh_selector.state == Status.SUCCESS
