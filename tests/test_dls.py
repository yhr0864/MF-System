import pytest
import time
from unittest.mock import MagicMock, patch
from src.devices.dls import DLS_Analyzer  # Replace with the actual module name


@patch("serial.Serial")
def test_initialize(mock_serial):
    """Test if DLS_Analyzer initializes the serial connection correctly and handles COM check."""

    # Mock serial instance
    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    # Mock successful COM check response
    mock_serial_instance.in_waiting = True
    mock_serial_instance.readline.return_value = b"K\n"

    # Create and initialize DLS_Analyzer
    dls = DLS_Analyzer(port="COM7", baudrate=9600, timeout=1)
    dls.initialize()

    # Assertions
    mock_serial.assert_called_once_with(port="COM7", baudrate=9600, timeout=1)
    assert dls.dls_ser is mock_serial.return_value

    # Ensure COM check command was sent
    mock_serial_instance.write.assert_called_once_with(bytes([0x31]))


@patch("serial.Serial")
def test_send_command_success(mock_serial):
    """Test send_command() successfully receives a response."""

    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    # Mock device response
    mock_serial_instance.in_waiting = True
    mock_serial_instance.readline.return_value = b"K\n"

    dls = DLS_Analyzer()
    dls.initialize(skip_com_check=True)

    response = dls.send_command(bytes([0x31]))

    assert response == "K"
    mock_serial_instance.write.assert_called_once_with(bytes([0x31]))


@patch("serial.Serial")
def test_send_command_timeout(mock_serial):
    """Test send_command() raises TimeoutError when no response is received."""

    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    # Simulate no response
    mock_serial_instance.in_waiting = False

    dls = DLS_Analyzer()
    dls.initialize(skip_com_check=True)

    with pytest.raises(
        TimeoutError, match="No response from DLS within the specified timeout."
    ):
        dls.send_command(cmd=bytes([0x31]), timeout=1)


@patch("serial.Serial")
def test_com_check_unexpected_response(mock_serial):
    """Test COM check failure due to unexpected response."""

    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    # Mock unexpected response
    mock_serial_instance.in_waiting = True
    mock_serial_instance.readline.return_value = b"X\n"

    dls = DLS_Analyzer()
    dls.initialize(skip_com_check=True)

    with pytest.raises(Exception, match="Unexpected response received: X"):
        dls.com_check()


@patch("serial.Serial")
def test_request_data(mock_serial):
    """Test request_data() with mocked device responses."""

    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    # Mock successful "run" response
    mock_serial_instance.in_waiting = True
    mock_serial_instance.readline.side_effect = [
        b"K\n",  # Run()
        b"K 0.5\n",  # Sample Loading
        b"K 10.0\n",  # Mean Volume Diameter
        b"K 8.0\n",  # Mean Area Diameter
        b"K 6.5\n",  # Mean Number Diameter
        b"K 10 1.0 20 2.0 30 3.0 40 4.0 50 5.0 60 6.0 70 7.0 80 8.0 90 9.0 95 10.0\n",  # Percentiles
    ]

    dls = DLS_Analyzer()
    dls.initialize(skip_com_check=True)

    assert dls.request_data(num_of_runs=1, data_file="test_output.csv") is True
