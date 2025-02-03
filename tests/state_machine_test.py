import pytest
from unittest.mock import MagicMock
from src.state_machine_boundary_con import (
    StateMachine,
)  # Adjust the import path as needed
from src.hardware import Hardware  # The real hardware class, to be mocked


@pytest.fixture
def mocked_hardware():
    """Fixture to provide a mocked Hardware instance."""
    mock = MagicMock(spec=Hardware)
    mock.initialize.return_value = None  # Mock initialize() so it does nothing
    return mock


@pytest.fixture
def state_machine(mocked_hardware, monkeypatch):
    """Fixture to create a StateMachine instance with mocked Hardware."""
    sm = StateMachine()

    # Replace the real hardware with the mocked version
    monkeypatch.setattr(sm, "hardware", mocked_hardware)

    return sm


def test_initialize(state_machine, mocked_hardware):
    """Test the initialize function."""
    state_machine.initialize()

    # Ensure that hardware.initialize() was called once
    mocked_hardware.initialize.assert_called_once()

    # Ensure the transition was triggered
    assert (
        state_machine.state == "before_cycle_stage_1"
    )  # Adjust according to your state transitions
