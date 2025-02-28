from ctypes import POINTER, cast, c_int, c_double, c_char
from collections import namedtuple

from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.uv_vis_lib.uvvissdk import _uvvisloadlib

uvvis_api = _uvvisloadlib.load_lib("SpecDLL")


class Uvvis:
    def lib_test(self) -> None:
        """
        Checks if library is communicating with user application.

        Prints an “Hello World”-type message.

        Returns:
            None
        """

        result = getattr(uvvis_api, "?LibTest@classSpec@specspace@@SAXXZ")
        return result()

    def scan_devices(self):
        """
        Scans for unconnected available Sarspec FLEX spectrometers.

        Returns:
            List[int]: A list with information regarding available FLEX devices.
                - First element: number of available unconnected devices
                - Subsequent pairs: Device ID and Device Type

            Device Types:
                - 0: Flex STD
                - 1: Flex RES+
        """

        result = getattr(uvvis_api, "?ScanDevices@classSpec@specspace@@SAPEAHXZ")
        result.restype = POINTER(c_int)
        arr_ptr = result()
        size = arr_ptr[0] * 2 + 1

        # Convert pointer to an array
        arr = cast(arr_ptr, POINTER(c_int * size)).contents
        return arr

    def get_serial(self, id: int) -> str:
        """
        Retrieves the serial number of an unconnected device.
        Note: It is not possible to use this function for connected devices.

        Args:
            id (int): Devices ID according to ScanDevices()

        Returns:
            str: Serial number of the specified device.
        """

        result = getattr(uvvis_api, "?GetSerial@classSpec@specspace@@SAPEBDH@Z")
        result.restype = POINTER(c_char)
        return result

    def connect(self, id: int) -> int:
        """
        Connects to Sarspec FLEX spectrometer.

        Args:
            id (int): Devices ID according to ScanDevices()

        Returns:
            int: FTHandle_ID if connection is successful, -1 if unsuccessful.
        """

        result = getattr(uvvis_api, "?Connect@classSpec@specspace@@SAHH@Z")
        return result(id)

    def disconnect(self, id: int) -> bool:
        """
        Disconnects from Sarspec FLEX spectrometer.

        Args:
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if disconnected successfully, False if failed.
        """

        result = getattr(uvvis_api, "?Disconnect@classSpec@specspace@@SA_NH@Z")
        return result(id)

    def switch_LED(self, switch: bool, id: int) -> bool:
        """
        Turns on/off the LED of device.

        Args:
            switch (bool): True to turn on, False to turn off
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if the command succeeded, False otherwise.
        """

        result = getattr(uvvis_api, "?LED@classSpec@specspace@@SA_N_NH@Z")
        return result(switch, id)

    def change_integration_time(self, int_time: int, id: int) -> bool:
        """
        Changes the integration time of the device.

        Args:
            int_time (int): Integration time in milliseconds
                - 3 to 214500 ms for FLEX RES+
                - 2 to 214500 ms for FLEX STD
        id (int): FTHandle_ID of the device

        Returns:
            bool: True if the time was changed successfully, False otherwise.
        """

        result = getattr(
            uvvis_api, "?ChangeIntegrationTime@classSpec@specspace@@SA_NHH@Z"
        )
        return result(int_time, id)

    def get_YData(self, external_trigger: bool, id: int):
        """
        Obtains a measurement.

        Args:
            external_trigger (bool):
                - True: Uses external trigger
                - False: Uses internal trigger
            id (int): FTHandle_ID of the device

        Returns:
            List[float]: Intensity values for each pixel.
        """

        result = getattr(uvvis_api, "?YData@classSpec@specspace@@SAPEAN_NH@Z")
        result.restype = POINTER(c_double)

        arr_ptr = result(external_trigger, id)
        size = 3648  # depends on Spectrometer Product Report

        # Convert pointer to an array
        arr = cast(arr_ptr, POINTER(c_double * size)).contents
        return arr

    def get_XData(self, c0: float, c1: float, c2: float, c3: float, id: int):
        """
        Gets wavelength array based on provided wavelength coefficients.

        Args:
            c0 (float): Wavelength coefficient c0
            c1 (float): Wavelength coefficient c1
            c2 (float): Wavelength coefficient c2
            c3 (float): Wavelength coefficient c3
            id (int): FTHandle_ID of the device

        Returns:
            list[float]: A list of wavelength values (in nm) for each pixel.

        Formula:
            Wavelength(PixelN) = c0 + c1 * PixelN + c2 * (PixelN ** 2) + c3 * (PixelN ** 3)
        """

        result = getattr(uvvis_api, "?XData@classSpec@specspace@@SAPEANNNNNH@Z")
        result.restype = POINTER(c_double)

        arr_ptr = result(c0, c1, c2, c3, id)
        size = 3648  # depends on Spectrometer Product Report

        # Convert pointer to an array
        arr = cast(arr_ptr, POINTER(c_double * size)).contents
        return arr

    def read_EEPROMCoeff(self, id: int) -> float:
        """
        Reads the coefficients from the EEPROM of device.

        Args:
            id (int): FTHandle_ID of the device

        Returns:
            list[float]: A list containing four wavelength coefficients [c0, c1, c2, c3].
        """

        result = getattr(uvvis_api, "?XData@classSpec@specspace@@SAPEANNNNNH@Z")
        result.restype = POINTER(c_double)

        arr_ptr = result(id)
        size = 4

        # Convert pointer to an array
        arr = cast(arr_ptr, POINTER(c_double * size)).contents
        return arr

    def switch_shutter(self, switch: bool, id: int) -> bool:
        """
        Closes or opens the shutter of device, if available.

        Args:
            switch (bool): True to close, False to open
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if successful, False otherwise.
        """

        result = getattr(uvvis_api, "?Shutter@classSpec@specspace@@SA_N_NH@Z")
        return result(switch, id)

    def trigger_out_on_off(self, switch: bool, id: int):
        """
        Enables or disables the device's trigger out function.

        Args:
            switch (bool): True to enable, False to disable
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if successful, False otherwise.
        """

        result = getattr(uvvis_api, "?TriggerOutOnOff@classSpec@specspace@@SA_NHH@Z")
        return result(switch, id)

    def trigger_in_enable(self, trigger_in_delay: int, id: int) -> bool:
        """
        Activates Trigger In mode, allowing measurements based on external triggers.

        Args:
            trigger_in_delay (int): Delay in microseconds before responding to trigger
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if activated, False otherwise.
        """

        result = getattr(uvvis_api, "?TriggerInEnable@classSpec@specspace@@SA_NHH@Z")
        return result(trigger_in_delay, id)

    def trigger_in_disable(self, id: int) -> bool:
        """
        Deactivates Trigger In mode.

        Args:
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if disabled successfully, False otherwise.
        """

        result = getattr(uvvis_api, "?TriggerInDisable@classSpec@specspace@@SA_NH@Z")
        return result(id)

    def prepare_SpecACK(self, id: int) -> bool:
        """
        Prepares the spectrometer for a new measurement using an external trigger.

        Args:
            id (int): FTHandle_ID of the device

        Returns:
            bool: True if successful, False otherwise.
        """

        result = getattr(uvvis_api, "?SpecACK@classSpec@specspace@@SA_NH@Z")
        return result(id)


if __name__ == "__main__":
    uvvis = Uvvis()
    arr = uvvis.scan_devices()

    print(len(arr))
