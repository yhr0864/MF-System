import time

import serial
from tqdm import tqdm
import pandas as pd

from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.utils import (
    RequestFailed,
    UnexpectedResponse,
    ErrorOccurred,
)


class DLSAdapter(IHardwareAdapter):
    """
    A class to interface with a DLS (Dynamic Light Scattering) analyzer through a serial connection.

    This class provides methods for initializing the serial connection, sending commands to
    the DLS device, and handling communication with the device. It is intended for controlling
    and interacting with a DLS analyzer through RS232 serial communication.

    Attributes:
        config (dict): The configuration file that defines serial port, baud rate and timeout.
    """

    def __init__(self, config: dict):
        self.port = config["port"]
        self.baudrate = config["baudrate"]
        self.timeout = config["timeout"]
        self._connection = None

    def initialize(self, skip_com_check=False) -> bool:
        """
        Initialize and check the serial connection to the DLS device.

        This method sets up the serial communication using the specified port,
        baudrate, and timeout. The connection is established via the `serial.Serial`
        interface, enabling communication with the device.

        Args:
            skip_com_check (bool): Flag to be used for testing only.

        Returns:
            bool: True if connect successfully, else False.
        """

        try:
            # Initialize the serial port
            self._connection = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout
            )

            # Check COM port
            if not skip_com_check:
                self.com_check()

            return True
        except ConnectionError:
            return False

    def execute(self, command: dict) -> str:
        if command["action"] == "select_measurement_setup":
            return self.select_measurement_setup(command["id"])
        elif command["action"] == "request_data":
            return self.request_data(command["num_of_runs"], command["save_path"])
        else:
            raise ValueError(f"Unsupported command: {command["action"]}")

    def shutdown(self) -> None:
        if self._connection.is_open:
            self._connection.close()

    def send_command(self, cmd: bytes, timeout=5) -> str:
        """
        Sends a command to the DLS device and waits for a response.

        This method writes the given command to the DLS device, waits for a response
        within the specified timeout period, and returns the feedback received from the
        device. If no response is received within the timeout, a `TimeoutError` is raised.

        Args:
            cmd (bytes): The command to send to the DLS device.
            timeout (int, optional): The maximum time to wait for a response, in seconds. Defaults to 5 seconds.

        Returns:
            str: The feedback received from the device, decoded as a UTF-8 string.

        Raises:
            TimeoutError: If no response is received within the specified timeout.
        """

        # Send command to DLS
        self._connection.write(cmd)

        start_time = time.time()

        # Wait for a response
        while time.time() - start_time < timeout:
            # Check if get feedback
            if self._connection.in_waiting:
                self.feedback = self._connection.readline().decode("utf-8").strip()
                if self.feedback:
                    return self.feedback
        else:
            raise TimeoutError("No response from DLS within the specified timeout.")

    def com_check(self):
        """
        Verifies that the RS232 communications link is active.

        This method sends a dummy command to ensure that the RS232 communications
        link is present and operational. If the device responds, communications
        are considered successfully established.

        Args:
            None

        Raises:
            UnexpectedResponse: If the device returns an unexpected response.
        """

        cmd = bytes([0x31])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("COM Check Successful")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def select_measurement_setup(self, setup_index: int):
        """
        Selects a measurement setup from the scheduler.

        This method selects a measurement setup by index (1, 2, ...) and applies
        the corresponding parameters to the next `setzero` or `run` command.
        The selected setup remains active for all subsequent measurements until
        either another measurement setup is selected or a local change to the
        measurement setup is made.

        Args:
            setup_index (int): The index of the measurement setup to select.

        Raises:
            RequestFailed: If the selection process fails and the device returns 'N'.
            UnexpectedResponse: If the device returns an unexpected response.
        """

        cmd = bytes([0x36, setup_index])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("Measurement Setup Selection Successful")
        elif feedback == "N":
            raise RequestFailed("Measurement Setup Selection Failed")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def set_zero(self):
        """
        Initiates the Setzero function for a measurement with no sample present.

        This method starts a Setzero process, which must complete before other
        commands can be sent. The status of the Setzero process is returned once
        it is finished.

        Args:
            None

        Raises:
            RequestFailed: If the Setzero process fails with 'High Background' (response 'N').
            UnexpectedResponse: If the device returns an unexpected response.
        """

        cmd = bytes([0x33])
        feedback = self.send_command(cmd=cmd, timeout=60)
        if feedback == "K":
            print("Set Zero Successful")
        elif feedback == "N":
            raise RequestFailed("Set Zero Failed: High Background")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def run(self):
        """
        Initiates a sample measurement run.

        This method starts a measurement with a sample present. No other commands
        can be sent until the HOST computer returns the measurement status. The
        method checks the response and raises exceptions if the run fails or an
        error occurs.

        Args:
            None

        Raises:
            RequestFailed: If the measurement run fails (response 'N').
            ErrorOccurred: If an error occurs on the HOST PC (response 'E').
            UnexpectedResponse: If the device returns an unexpected response.
        """

        cmd = bytes([0x34])
        feedback = self.send_command(cmd=cmd, timeout=500)
        if feedback == "K":
            pass
        elif feedback == "N":
            raise RequestFailed("Sample Measurement Failed")
        elif feedback == "E":
            raise ErrorOccurred("Error has occurred on the HOST PC")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def request_data(self, num_of_runs: int, save_path: str) -> bool:
        """
        Perform multiple measurements, collect requested data, and save results in a .csv file.

        This method runs multiple measurements, collects data for each measurement (e.g.,
        mean diameters and percentiles), and stores the results in a specified CSV file.
        After completing the measurements, it calculates and appends average values for each
        data point.

        Args:
            num_of_runs (int): The number of measurements to perform.
            save_path (str): The file path where the data will be saved.

        Returns:
            bool: The feedback is True if requested data is ready, else False.

        Raises:
            RequestFailed: If any of the measurements fail or return invalid data (response 'N').
            UnexpectedResponse: If the device returns an unexpected response.
        """

        DATA_COMMANDS = {
            "Sample Loading": bytes([0x37, 1]),
            "Mean Volume Diameter": bytes([0x37, 2]),
            "Mean Area Diameter": bytes([0x37, 3]),
            "Mean Number Diameter": bytes([0x37, 4]),
            "Percentiles": bytes([0x37, 5]),
        }

        headers = [
            "Time",
            "Run",
            "Loading Index",
            "Mean volume diameter",
            "Mean area diameter",
            "Mean number diameter",
            "d(10%)",
            "d(20%)",
            "d(30%)",
            "d(40%)",
            "d(50%)",
            "d(60%)",
            "d(70%)",
            "d(80%)",
            "d(90%)",
            "d(95%)",
        ]

        # Flag
        isFinished = False

        # DataFrame to store all measurements
        results_df = pd.DataFrame(columns=headers)

        for run_id in tqdm(range(num_of_runs), desc="Measurements Running: "):
            # Run measurement once
            self.run()
            data_line = [time.asctime(), run_id + 1]

            for cmd in DATA_COMMANDS.values():
                feedback = self.send_command(cmd=cmd)
                feedback_list = str(feedback).split()

                if feedback_list[0] == "K":
                    # Extract the Percentile Value from Percentile
                    if len(feedback_list) != 2:
                        data_line.extend(feedback_list[2::2])
                    # Extract Data Value
                    else:
                        data_line.extend(feedback_list[1:])
                elif feedback_list[0] == "N":
                    raise RequestFailed("Invalid Data Request")
                else:
                    raise UnexpectedResponse(f"Unexpected response: {feedback_list[0]}")

            # Add the new row with current measurement to the DataFrame
            results_df.loc[len(results_df)] = data_line

        # Calculate mean values for numeric columns
        numeric_columns = headers[2:]  # Exclude "Time", "Run" and "Signal Quality"
        mean_values = results_df[numeric_columns].astype(float).mean()

        avg_row = [
            time.asctime(),
            "Avg.",
            mean_values.round(2).iloc[0],
        ] + mean_values.round(1).tolist()[1:]

        # Append the average row to the DataFrame
        results_df.loc[len(results_df)] = avg_row

        # Add new column for signal quality
        signal_quality = [
            (
                "Over-Dilution"
                if float(i) < 0.1
                else "Under-Dilution" if float(i) > 100 else "Good"
            )
            for i in results_df["Loading Index"]
        ]
        results_df.insert(loc=3, column="Signal Quality", value=signal_quality)

        # Save the results to a CSV file
        results_df.to_csv(save_path, index=False)

        isFinished = True
        print(f"Measurement finished, data is saved under {save_path}")
        return isFinished


if __name__ == "__main__":
    dls = DLSAdapter({"port": "COM7", "baudrate": 9600, "timeout": 1})
    print("start init")
    dls.initialize()
    print("finish init")

    time.sleep(1)

    dls.execute({"action": "select_measurement_setup", "id": 5})

    time.sleep(1)
    # # # dls.set_zero()

    dls.execute({"action": "request_data", "num_of_runs": 3})
