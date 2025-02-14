import pytest
from unittest.mock import MagicMock, patch, call

from mf_system.hardware.devices.pump import SyringePump


@pytest.fixture
def mock_pump():
    """Fixture to create a mocked SyringePump instance."""
    with (
        patch("mf_system.hardware.devices.pump_lib.qmixsdk.qmixbus.Bus") as mock_bus,
        patch("mf_system.hardware.devices.pump_lib.qmixsdk.qmixpump.Pump") as mock_pump,
        patch(
            "mf_system.hardware.devices.pump_lib.qmixsdk.qmixanalogio.AnalogInChannel"
        ) as mock_analog,
    ):

        pump = SyringePump(
            pump_name="TestPump",
            pressure_limit=100.0,
            inner_diameter_mm=10.0,
            max_piston_stroke_mm=50.0,
        )
        # Mock the bus, pump and pressure_channel objects
        pump.bus = MagicMock()
        pump.pump = MagicMock()
        pump.pressure_channel = MagicMock()
        pump.valve = MagicMock()

        # Explicitly mock methods
        pump.wait_dosage_finished = MagicMock(return_value=True)
        pump.switch_valve_to = MagicMock()
        pump.switch_valve_to.side_effect = lambda value: setattr(
            pump.valve, "actual_valve_position", value
        )

        return pump


@pytest.fixture
def mock_valve():
    """This one is only used for test_switch_valve()."""
    with (
        patch("mf_system.hardware.devices.pump_lib.qmixsdk.qmixbus.Bus") as mock_bus,
        patch("mf_system.hardware.devices.pump_lib.qmixsdk.qmixpump.Pump") as mock_pump,
        patch(
            "mf_system.hardware.devices.pump_lib.qmixsdk.qmixanalogio.AnalogInChannel"
        ) as mock_analog,
    ):

        pump = SyringePump(
            pump_name="TestPump",
            pressure_limit=100.0,
            inner_diameter_mm=10.0,
            max_piston_stroke_mm=50.0,
        )
        # Mock the valve only
        pump.valve = MagicMock()

        return pump


# Test cases
def test_initialize(mock_pump, mock_valve):
    """Test pump initialization."""
    mock_pump.pump.is_in_fault_state.return_value = False
    mock_pump.pump.is_enabled.return_value = False
    mock_pump.pump.has_valve.return_value = True
    mock_pump.pressure_channel.read_status.return_value = 1
    mock_pump.pressure_channel.get_scaling_param.return_value = (0.05, -25)

    # Call initialize
    mock_pump.initialize()

    # Assertions
    mock_pump.pump.clear_fault.assert_not_called()  # No fault state
    mock_pump.pump.enable.assert_called_once_with(True)
    mock_pump.pump.set_syringe_param.assert_called_once_with(10.0, 50.0)
    # mock_valve.valve.switch_valve_to_position.assert_called_once_with(0)
    assert mock_pump.valve.actual_valve_position == 0
    mock_pump.pressure_channel.enable_software_scaling.assert_called_once_with(True)
    mock_pump.pressure_channel.set_scaling_param.assert_called_once_with(0.05, -25)
    mock_pump.pump.set_volume_unit.assert_called_once()
    mock_pump.pump.set_flow_unit.assert_called_once()


def test_aspirate(mock_pump):
    """Test pump aspiration."""
    mock_pump.wait_dosage_finished.return_value = True

    # Call aspirate
    result = mock_pump.aspirate(volume=10.0, flow=5.0)

    # Assertions
    mock_pump.pump.aspirate.assert_called_once_with(10.0, 5.0)
    mock_pump.wait_dosage_finished.assert_called_once_with(600)
    assert result is True


def test_dispense(mock_pump):
    """Test pump dispension."""
    mock_pump.wait_dosage_finished.return_value = True

    # Call dispense
    result = mock_pump.dispense(volume=10.0, flow=5.0)

    # Assertions
    mock_pump.pump.dispense.assert_called_once_with(10.0, 5.0)
    mock_pump.wait_dosage_finished.assert_called_once_with(600)
    assert result is True


def test_refill(mock_pump):
    """Test pump refill."""
    mock_pump.wait_dosage_finished.return_value = True

    # Call refill
    result = mock_pump.refill(flow=5.0)

    # Assertions
    mock_pump.pump.generate_flow.assert_called_once_with(-5.0)
    mock_pump.wait_dosage_finished.assert_called_once_with(1200)
    assert result is True


def test_empty(mock_pump):
    """Test pump empty."""
    mock_pump.wait_dosage_finished.return_value = True

    # Call empty
    result = mock_pump.empty(flow=5.0)

    # Assertions
    mock_pump.pump.generate_flow.assert_called_once_with(5.0)
    mock_pump.wait_dosage_finished.assert_called_once_with(1200)
    assert result is True


def test_switch_valve(mock_valve):
    """Test valve switching functionality."""
    mock_valve.valve.actual_valve_position.return_value = 1

    # Call switch_valve_to
    mock_valve.switch_valve_to(1)

    # Assertions
    mock_valve.valve.switch_valve_to_position.assert_called_once_with(1)
    mock_valve.valve.actual_valve_position.assert_called_once()
    assert mock_valve.valve.actual_valve_position() == 1

    mock_valve.valve.actual_valve_position.return_value = 2

    # Call switch_valve_to again
    mock_valve.switch_valve_to(2)

    # Assertions
    assert mock_valve.valve.actual_valve_position() == 2


def test_stop_pump(mock_pump):
    """Test stopping the pump."""

    # Call stop_pump
    mock_pump.stop_pump()

    # Assertions
    mock_pump.pump.stop_pumping.assert_called_once()


def test_stop_all_pumps():
    """Test stopping all pumps."""

    # Mock the static method
    with patch(
        "mf_system.hardware.devices.pump_lib.qmixsdk.qmixpump.Pump.stop_all_pumps"
    ) as mock_stop_all:

        # Call stop_all_pumps
        SyringePump.stop_all_pumps()

        # Assertions
        mock_stop_all.assert_called_once()


def test_capi_close(mock_pump):
    """Test closing the bus communication."""
    mock_pump._bus_opened = True

    # Call capi_close
    mock_pump.capi_close()

    # Assertions
    mock_pump.bus.stop.assert_called_once()
    mock_pump.bus.close.assert_called_once()
    assert mock_pump._bus_opened is True
