import pytest
from unittest.mock import Mock, patch, MagicMock

from src.state_machine_boundary_con import StateMachine


@pytest.fixture
def mock_hardware_components():
    # Create mocks for all hardware components
    mock_syringe = MagicMock()
    mock_syringe.valve = MagicMock()

    mock_table = MagicMock()
    mock_table.motor = MagicMock()

    mock_uv = MagicMock()
    mock_dls = MagicMock()

    return {
        "syringe": mock_syringe,
        "table": mock_table,
        "uv": mock_uv,
        "dls": mock_dls,
    }


@pytest.fixture
def mock_hardware(mock_hardware_components):
    mock = MagicMock()

    # Set up the hardware methods to return True
    mock.initialize.return_value = True
    mock.tray_to_pump.return_value = True
    mock.rotate_table_p.return_value = True
    mock.rotate_table_m.return_value = True
    mock.fill_bottle.return_value = True
    mock.pump_to_measure.return_value = True
    mock.measure_UV.return_value = True
    mock.measure_DLS.return_value = True
    mock.measure_to_tray.return_value = True

    # Attach mocked components
    mock.syringe = mock_hardware_components["syringe"]
    mock.table = mock_hardware_components["table"]
    mock.uv = mock_hardware_components["uv"]
    mock.dls = mock_hardware_components["dls"]

    return mock


@pytest.fixture
def state_machine(mock_hardware, mock_hardware_components):
    # Create a list of patches for all potential hardware imports
    patches = [
        patch("src.hardware.Hardware", return_value=mock_hardware),
        patch(
            "src.devices.pump.SyringePump",
            return_value=mock_hardware_components["syringe"],
        ),
        patch(
            "src.devices.arduino.ArduinoBoard",
            return_value=mock_hardware_components["table"],
        ),
        # patch("src.devices.uv_vis.UV_Vis", return_value=mock_hardware_components["uv"]),
        patch(
            "src.devices.dls.DLS_Analyzer", return_value=mock_hardware_components["dls"]
        ),
    ]

    # Apply all patches
    for p in patches:
        p.start()

    machine = StateMachine()

    # Add cleanup to stop all patches
    yield machine

    for p in patches:
        p.stop()


def test_initialization(state_machine, mock_hardware):
    # Test initialize state
    assert state_machine.state == "initialize"
    state_machine.initialize()
    mock_hardware.initialize.assert_called_once()
    assert state_machine.state == "before_cycle_stage_1"


def test_before_cycle_stage_1(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_1"
    state_machine.before_cycle_stage_1()
    mock_hardware.tray_to_pump.assert_called_once()
    assert state_machine.current_num_bottles == 6  # Started with 7, decreased by 1


def test_before_cycle_stage_2(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_2"
    state_machine.before_cycle_stage_2()
    mock_hardware.rotate_table_p.assert_called_once()


def test_before_cycle_stage_3_with_multiple_bottles(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_3"
    state_machine.num_bottles = 3
    state_machine.before_cycle_stage_3()
    mock_hardware.fill_bottle.assert_called_once()
    mock_hardware.tray_to_pump.assert_called_once()


def test_before_cycle_stage_3_with_single_bottle(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_3"
    state_machine.num_bottles = 1
    state_machine.before_cycle_stage_3()
    mock_hardware.fill_bottle.assert_called_once()
    mock_hardware.tray_to_pump.assert_not_called()


def test_cycle_stage_1_experiment_finish(state_machine, mock_hardware):
    state_machine.state = "cycle_stage_1"
    state_machine.num_bottles = 1
    with pytest.raises(SystemExit):
        state_machine.cycle_stage_1()
    mock_hardware.measure_to_tray.assert_called_once()


def test_parallel_actions_in_stage_13(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_13"
    state_machine.num_bottles = 4
    state_machine.before_cycle_stage_13()
    mock_hardware.fill_bottle.assert_called_once()
    mock_hardware.pump_to_measure.assert_called_once()
    mock_hardware.measure_DLS.assert_called_once()
    mock_hardware.measure_UV.assert_called_once()


def test_bottle_count_tracking(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_1"
    initial_bottles = state_machine.current_num_bottles
    state_machine.before_cycle_stage_1()
    assert state_machine.current_num_bottles == initial_bottles - 1


def test_table_rotation_feedback(state_machine, mock_hardware):
    state_machine.state = "before_cycle_stage_2"
    mock_hardware.rotate_table_p.return_value = True
    state_machine.before_cycle_stage_2()
    assert state_machine.feedback is None
    assert state_machine.state == "before_cycle_stage_3"


def test_experiment_completion_conditions(state_machine, mock_hardware):
    # Test different bottle counts that should trigger experiment completion
    test_cases = [
        ("cycle_stage_1", 1),
        ("after_cycle_stage_2", 2),
        ("after_cycle_stage_5", 3),
        ("after_cycle_stage_7", 4),
        ("after_cycle_stage_9", 5),
    ]

    for state, bottles in test_cases:
        state_machine.state = state
        state_machine.num_bottles = bottles
        with pytest.raises(SystemExit):
            getattr(state_machine, state)()
