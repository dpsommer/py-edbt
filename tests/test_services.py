import asyncio
import time

import pytest

import edbt

from .mocks import AlwaysTrue, RunningTask, SuccessTask

_TEST_KEY = "test"
_NAMESPACE = "test_services"


@pytest.fixture
def rh_selector():
    selector = edbt.Selector()
    selector.add_child(
        edbt.RequestHandler(
            key=_TEST_KEY, namespace=_NAMESPACE, parent=selector, child=SuccessTask()
        )
    )
    selector.add_child(RunningTask())
    return selector


@pytest.fixture(autouse=True)
async def open_mailroom():
    edbt.mail_room.start()
    yield edbt.mail_room
    edbt.mail_room.stop()


async def test_check_mailbox(rh_selector: edbt.Selector):
    tree = edbt.BehaviourTree(rh_selector)

    tree.tick()

    edbt.mail_room.send_message(
        edbt.Message(
            sender=None,
            receiver=_NAMESPACE,
            request=(_TEST_KEY, ()),
            condition=AlwaysTrue,
            timeout=time.time_ns() + (2 * 1_000_000_000),
        )
    )
    await asyncio.sleep(0.2)

    tree.tick()

    assert rh_selector.state == edbt.Status.SUCCESS
