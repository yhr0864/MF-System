import pytest
from unittest.mock import MagicMock, call
from mf_system.hardware.hardware import Hardware
from mf_system.hardware.devices.pump import SyringePump
from mf_system.hardware.devices.utils import RequestFailed


@pytest.fixture
def mock_hardware_config():
    return {
        "Gantry": {"ip": "test_ip", "port": "test_port"},
        "Arduino": {"port": "test_port", "baudrate": 9600, "timeout": 1},
        "DLS": {"port": "COM1", "baudrate": 9600, "timeout": 1},
        "Pumps": {
            "pump1": {
                "name": "Pump1",
                "pressure_limit": 100,
                "inner_diameter_mm": 10,
                "max_piston_stroke_mm": 50,
                "flow": 5,
            },
            "pump2": {
                "name": "Pump2",
                "pressure_limit": 100,
                "inner_diameter_mm": 10,
                "max_piston_stroke_mm": 50,
                "flow": 5,
            },
        },
    }


@pytest.fixture
def mock_sample_data():
    return {
        "num_samples": 1,
        "out_flow": 10,
        "samples": {
            "1": {
                "volume": 100,
                "proportion": [1, 1],
                "solution": ["A", "B"],
                "pumps": ["pump1", "pump2"],
            }
        },
    }


# Mock the Hardware class
@pytest.fixture
def hardware(mocker, mock_hardware_config, mock_sample_data):
    # Mock the _load_config method to return test configs
    mocker.patch.object(
        Hardware,
        "_load_config",
        side_effect=[mock_hardware_config, mock_sample_data],
    )

    # Mock _initialize_pumps to avoid hardware calls
    mocker.patch.object(
        Hardware,
        "_initialize_pumps",
        return_value={
            "pump1": MagicMock(spec=SyringePump),
            "pump2": MagicMock(spec=SyringePump),
        },
    )

    hw = Hardware()

    # Mock device instances
    hw.gantry = MagicMock()
    hw.arduino = MagicMock()
    hw.dls = MagicMock()
    return hw


# Test cases
def test_initialize(hardware):
    hardware.arduino.send_command.side_effect = [
        "Home motor1",
        "Home motor2",
        "Home cylinder2",
        "Home cylinder1",
    ]
    hardware.initialize()

    hardware.gantry.initialize.assert_called_once()
    hardware.arduino.initialize.assert_called_once()
    hardware.dls.initialize.assert_called_once()
    for pump in hardware.pumps.values():
        pump.initialize.assert_called_once()

    hardware.arduino.send_command.assert_has_calls(
        [
            call("motor1 home"),
            call("motor2 home"),
            call("cylinder2 home"),
            call("cylinder1 home"),
        ],
        any_order=False,
    )


def test_prepare_pump(hardware):
    hardware.prepare_pump()
    hardware.pumps["pump1"].aspirate.assert_called_with(50.0, 5.0)
    hardware.pumps["pump2"].aspirate.assert_called_with(50.0, 5.0)


def test_fill_bottle(hardware):
    hardware.fill_bottle()
    hardware.pumps["pump1"].dispense.assert_called_with(50.0, 5.0)
    hardware.pumps["pump2"].dispense.assert_called_with(50.0, 5.0)
    assert hardware.sample_id == 1


def test_measure_DLS_success(hardware):
    hardware.arduino.send_command.side_effect = [
        "Cylinder2 Retraction Finished",
        "Cylinder2 Extension Finished",
    ]
    hardware.dls.request_data.return_value = True
    result = hardware.measure_DLS(1, 3, "test_path")

    hardware.dls.select_measurement_setup.assert_called_with(setup_index=1)
    hardware.dls.request_data.assert_called_with(num_of_runs=3, data_file="test_path")
    assert result == "Cylinder2 Extension Finished"


def test_measure_DLS_failure(hardware):
    hardware.arduino.send_command.return_value = "Failed"
    with pytest.raises(RequestFailed):
        hardware.measure_DLS(1, 3, "test_path")
    hardware.dls.select_measurement_setup.assert_not_called()


def test_movement_methods(hardware, capsys):
    test_coord = ((0, 0), (1, 1))
    movement_methods = [
        hardware.tray_to_pump,
        hardware.tray_to_measure,
        hardware.pump_to_measure,
        hardware.pump_to_tray,
        hardware.measure_to_tray,
    ]
    for method in movement_methods:
        method(test_coord)
        captured = capsys.readouterr()
        assert "to" in captured.out


def test_config_load_failure(mocker):
    mocker.patch.object(
        Hardware,
        "_load_config",
        side_effect=FileNotFoundError("File not found"),
    )
    with pytest.raises(FileNotFoundError):
        Hardware()
