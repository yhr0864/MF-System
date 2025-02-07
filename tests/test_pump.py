import pytest
import time
from unittest.mock import MagicMock, patch
from src.hardware.devices.pump import SyringePump


@pytest.fixture
def mock_pump():
    """Fixture to create a mocked SyringePump instance."""
    with (
        patch("src.hardware.devices.pump_lib.qmixsdk.qmixbus.Bus") as mock_bus,
        patch("src.hardware.devices.pump_lib.qmixsdk.qmixpump.Pump") as mock_pump,
        patch(
            "src.hardware.devices.pump_lib.qmixsdk.qmixanalogio.AnalogInChannel"
        ) as mock_analog,
    ):

        # Mock Bus
        mock_bus_instance = MagicMock()
        mock_bus.return_value = mock_bus_instance

        # Mock Pump
        mock_pump_instance = MagicMock()
        mock_pump.return_value = mock_pump_instance
        mock_pump_instance.get_device_name.return_value = "TestPump"
        mock_pump_instance.has_valve.return_value = True  # Ensure valve is available

        # Mock Valve
        mock_valve = MagicMock()
        mock_pump_instance.get_valve.return_value = mock_valve
        mock_valve.switch_valve_to_position.side_effect = lambda pos: setattr(
            mock_valve, "current_position", pos
        )
        mock_valve.actual_valve_position.side_effect = lambda: getattr(
            mock_valve, "current_position", 0
        )

        # Mock Analog Channel (Pressure Sensor)
        mock_analog_instance = MagicMock()
        mock_analog.return_value = mock_analog_instance
        mock_analog_instance.read_status.return_value = True
        mock_analog_instance.read_input.return_value = 10.0  # Simulated pressure

        # Create SyringePump instance
        pump = SyringePump(
            "TestPump",
            pressure_limit=100,
            inner_diameter_mm=10,
            max_piston_stroke_mm=50,
        )
        pump.initialize()
        pump.bus = mock_bus_instance

        return pump


def test_initialize(mock_pump):
    """Test pump initialization."""
    assert mock_pump.valve is not None  # Ensure valve is set
    assert mock_pump.pump.is_enabled.called  # Check pump was enabled
    assert mock_pump.pressure_channel.read_status.called  # Pressure sensor checked


def test_switch_valve(mock_pump):
    """Test valve switching functionality."""
    mock_pump.switch_valve_to(1)
    assert mock_pump.pump.get_valve().actual_valve_position() == 1

    mock_pump.switch_valve_to(2)
    assert mock_pump.pump.get_valve().actual_valve_position() == 2


def test_stop_pump(mock_pump):
    """Test stopping the pump."""
    mock_pump.stop_pump()
    assert mock_pump.pump.stop_pumping.called  # Ensure stop function was called


def test_stop_all_pumps():
    """Test stopping all pumps."""
    with patch(
        "src.hardware.devices.pump_lib.qmixsdk.qmixpump.Pump.stop_all_pumps"
    ) as mock_stop_all:
        SyringePump.stop_all_pumps()
        mock_stop_all.assert_called_once()


def test_capi_close(mock_pump):
    """Test closing the bus communication."""
    mock_pump.capi_close()
    assert mock_pump.bus.stop.called  # Ensure bus stop was called
    assert mock_pump.bus.close.called  # Ensure bus close was called
