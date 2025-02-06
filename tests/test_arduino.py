import pytest
from unittest.mock import MagicMock, patch

from src.devices.arduino import ArduinoBoard


@patch("serial.Serial")
def test_initialize(mock_serial):
    """Test if ArduinoBoard initializes the serial connection correctly."""

    board = ArduinoBoard(port="COM14", baudrate=9600, timeout=0.1)

    board.initialize()

    mock_serial.assert_called_once_with(port="COM14", baudrate=9600, timeout=0.1)
    assert board.arduino is mock_serial.return_value


@patch("serial.Serial")
def test_send_command_success(mock_serial):
    """Test send_command() successfully receives a response."""

    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    board = ArduinoBoard()
    board.initialize()

    mock_serial_instance.in_waiting = True
    mock_serial_instance.readline.return_value = b"OK\n"

    response = board.send_command("motor2 home")

    assert response == "OK"
    mock_serial_instance.write.assert_called_once_with(b"motor2 home")


@patch("serial.Serial")
def test_send_command_timeout(mock_serial):
    """Test send_command() raises TimeoutError when no response is received."""

    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance

    board = ArduinoBoard()
    board.initialize()

    mock_serial_instance.in_waiting = False

    with pytest.raises(
        TimeoutError, match="No response from Arduino within the specified timeout."
    ):
        board.send_command("motor2 home", timeout=1)
