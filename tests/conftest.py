import pytest

from edbt import blackboard


@pytest.fixture(autouse=True)
def wipe_blackboard():
    blackboard.clear()
    blackboard._observers.clear()
