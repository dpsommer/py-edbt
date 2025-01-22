import pytest

from edbt import BehaviourTree


@pytest.fixture
def tree() -> BehaviourTree:
    return BehaviourTree()
