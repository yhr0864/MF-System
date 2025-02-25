import serial
import time
from concurrent.futures import ThreadPoolExecutor

from mf_system.hardware.devices.interface import IHardwareAdapter


class ArduinoAdapter(IHardwareAdapter):
    def __init__(self, config: dict):
        self.port = config["port"]
        self.baudrate = config["baudrate"]
        self.timeout = config["timeout"]
        self._connection = None

    def initialize(self) -> bool:
        try:
            self._connection = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout
            )
            time.sleep(1)

            commands = [
                {"action": "motor1 home"},
                {"action": "motor2 home"},
                {"action": "cylinder1 home"},
                {"action": "cylinder2 home"},
            ]

            for command in commands:
                self.execute(command)
            return True
        except ConnectionError:
            return False

    def execute(self, command: str) -> str:
        return self.send_command(command["action"])

    def send_command(self, cmd: str, timeout=30) -> str:
        # Send command to Arduino
        self._connection.write(bytes(cmd, "utf-8"))

        start_time = time.time()
        # Wait for a response
        while time.time() - start_time < timeout:
            # Check if get feedback
            if self._connection.in_waiting:
                self.feedback = self._connection.readline().decode("utf-8").strip()
                if self.feedback:
                    return self.feedback
        else:
            raise TimeoutError("No response from Arduino within the specified timeout.")

    def shutdown(self) -> None:
        if self._connection.is_open:
            self._connection.close()


if __name__ == "__main__":
    arduino = ArduinoAdapter({"port": "COM14", "baudrate": 9600, "timeout": 0.1})
    res = arduino.initialize()
    time.sleep(1)

    # f = arduino.send_command("motor1 home \n motor2 home")
    # f = arduino.execute({"action": "motor1 home"})
    # f = arduino.execute({"action": "motor2 home"})
    # f = arduino.execute({"action": "cylinder1 home"})
    # print(f, res)
    # arduino.shutdown()
