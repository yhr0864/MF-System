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
            # Home position parallelly
            with ThreadPoolExecutor() as executor:
                f1 = executor.submit(self.execute, {"action": "motor1 home"})
                f2 = executor.submit(self.execute, {"action": "motor2 home"})
                f3 = executor.submit(self.execute, {"action": "cylinder1 home"})
                f4 = executor.submit(self.execute, {"action": "cylinder2 home"})
                f1.result()
                f2.result()
                f3.result()
                f4.result()
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
    arduino.initialize()
    time.sleep(1)

    # f = arduino.send_command("motor1 home \n motor2 home")
    command = {"action": "motor2 home"}
    f = arduino.execute(command)
    print(f)
