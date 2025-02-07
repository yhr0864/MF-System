import pytest
from unittest import mock
from src.logic.state_machine_boundary_con import StateMachine
from src.hardware.hardware import Hardware


@pytest.fixture
def mock_hardware():
    mock_hardware = mock.MagicMock(spec=Hardware)

    mock_hardware.initialize.return_value = None

    mock_hardware.tray_to_pump.return_value = None
    mock_hardware.fill_bottle.return_value = None
    mock_hardware.rotate_table_p.return_value = True
    mock_hardware.rotate_table_m.return_value = True
    mock_hardware.pump_to_measure.return_value = None
    mock_hardware.measure_UV.return_value = None
    mock_hardware.measure_DLS.return_value = None
    mock_hardware.measure_to_tray.return_value = None

    return mock_hardware


@pytest.fixture
def state_machine(mock_hardware):
    # Initialize the StateMachine with the mocked hardware
    sm = StateMachine(num_bottles=7, hardware=mock_hardware)

    return sm


def test_initialize(state_machine, mock_hardware):
    # Test the initialize state
    state_machine.initialize()

    # Verify that the hardware initialize method was called
    mock_hardware.initialize.assert_called_once()

    # Verify that the state transition happens as expected
    assert state_machine.state == "before_cycle_stage_1"


def test_before_cycle_stage_1(state_machine, mock_hardware):
    state_machine.before_cycle_stage_1()

    mock_hardware.tray_to_pump.assert_called_once()

    assert state_machine.current_num_bottles == 6


def test_before_cycle_stage_2(state_machine, mock_hardware):
    state_machine.before_cycle_stage_2()

    mock_hardware.rotate_table_p.assert_called_once()


def test_before_cycle_stage_3(state_machine, mock_hardware):
    state_machine.before_cycle_stage_3()

    mock_hardware.fill_bottle.assert_called_once()

    assert state_machine.current_num_bottles == 6


def test_auto_run(state_machine, mock_hardware):
    # Test the auto_run method
    with mock.patch.object(state_machine, "auto_run", return_value=None):
        state_machine.auto_run()
        state_machine.auto_run.assert_called_once()
