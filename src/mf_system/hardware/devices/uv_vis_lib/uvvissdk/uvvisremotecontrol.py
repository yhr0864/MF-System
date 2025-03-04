import ctypes
from collections import namedtuple

from mf_system.hardware.devices.utils import RequestFailed
from mf_system.hardware.devices.uv_vis_lib.uvvissdk import _uvvisloadlib

uvvis_api = _uvvisloadlib.load_lib("SpecDLL")

# The function names are encrypted within the DLL
encrypted_function_names = {
    "ChangeIntegrationTime": "?ChangeIntegrationTime@classSpec@specspace@@SA_NHH@Z",
    "Connect": "?Connect@classSpec@specspace@@SAHH@Z",
    "Disconnect": "?Disconnect@classSpec@specspace@@SA_NH@Z",
    "GetSerial": "?GetSerial@classSpec@specspace@@SAPEBDH@Z",
    "LED": "?LED@classSpec@specspace@@SA_N_NH@Z",
    "LibTest": "?LibTest@classSpec@specspace@@SAXXZ",
    "ReadEEPROMCoeff": "?ReadEEPROMCoeff@classSpec@specspace@@SAPEANH@Z",
    "ScanDevices": "?ScanDevices@classSpec@specspace@@SAPEAHXZ",
    "Shutter": "?Shutter@classSpec@specspace@@SA_N_NH@Z",
    "SpecACK": "?SpecACK@classSpec@specspace@@SA_NH@Z",
    "TriggerInDisable": "?TriggerInDisable@classSpec@specspace@@SA_NH@Z",
    "TriggerInEnable": "?TriggerInEnable@classSpec@specspace@@SA_NHH@Z",
    "TriggerOutOnOff": "?TriggerOutOnOff@classSpec@specspace@@SA_NHH@Z",
    "XData": "?XData@classSpec@specspace@@SAPEANNNNNH@Z",
    "YData": "?YData@classSpec@specspace@@SAPEAN_NH@Z",
}

# Tracking connections
connected = {"FThandle": "ID"}
scanDevices = [False]

# Types of FLEX devices
FLEX_types = ["STD", "RES+"]


class UVvis:
    def lib_test(self) -> None:
        """
        Checks if library is communicating with user application.

        Prints an “Hello World”-type message.

        Returns:
            None
        """

        # Setting the LibTest function
        function = getattr(uvvis_api, encrypted_function_names["LibTest"])
        function.argtypes = []
        function.restype = None

        return function()

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

        # Setting the ScanDevices function
        function = getattr(uvvis_api, encrypted_function_names["ScanDevices"])
        function.argtypes = []
        function.restype = ctypes.POINTER(ctypes.c_int)

        # Determine the amount of data to output
        size = function()[0] * 2 + 1

        # Set flag for ScanDevice use
        try:
            scanDevices.remove(False)
            scanDevices.append(True)
        except ValueError:
            pass

        return function()[:size]

    def get_serial(self, id: int) -> str:
        """
        Retrieves the serial number of an unconnected device.
        Note: It is not possible to use this function for connected devices.

        Args:
            id (int): Devices ID according to ScanDevices()

        Returns:
            str: Serial number of the specified device.
        """

        if scanDevices[0]:  # ScanDevices() needs to be run first
            if id not in connected.values():

                # Setting the GetSerial function
                function = getattr(uvvis_api, encrypted_function_names["GetSerial"])
                function.argtypes = [ctypes.c_int]
                function.restype = ctypes.c_char_p

                # Returns the serial number converted from bytes type to str
                return str(function(id))[2:-1]
            else:
                raise RequestFailed("This function cannot be used in connected devices")
        else:
            raise RequestFailed("Use ScanDevices() first!")

    def connect(self, id: int) -> int:
        """
        Connects to Sarspec FLEX spectrometer.

        Args:
            id (int): Devices ID according to ScanDevices()

        Returns:
            int: FTHandle_ID if connection is successful, -1 if unsuccessful.
        """

        # Setting the Connect function
        function = getattr(uvvis_api, encrypted_function_names["Connect"])
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.c_int

        # Attempts to connect
        FThandle_ID = function(id)

        # Saving the FThandle_ID in case of a successful connection
        if FThandle_ID != -1:
            connected[FThandle_ID] = id

        return FThandle_ID

    def disconnect(self, FTHandle_ID: int) -> bool:
        """
        Disconnects from Sarspec FLEX spectrometer.

        Args:
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            success (bool): True if disconnected successfully, False if failed.
        """

        # Setting the Disconnect function
        function = getattr(uvvis_api, encrypted_function_names["Disconnect"])
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.c_bool

        # Attempts to disconnect
        success = function(FTHandle_ID)

        # Removes the device from the connected dictionary
        if success:
            connected.pop(FTHandle_ID)

        # Returns whether it was successful or not (True/False)
        return success

    def switch_LED(self, switch: bool, FTHandle_ID: int) -> bool:
        """
        Turns on/off the LED of device.

        Args:
            switch (bool): True to turn on, False to turn off
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if the command succeeded, False otherwise.
        """

        # Setting the LED function
        function = getattr(uvvis_api, encrypted_function_names["LED"])
        function.argtypes = [ctypes.c_bool, ctypes.c_int]
        function.restype = ctypes.c_bool

        return function(switch, FTHandle_ID)

    def change_integration_time(self, int_time: int, FTHandle_ID: int) -> bool:
        """
        Changes the integration time of the device.

        Args:
            int_time (int): Integration time in milliseconds
                - 3 to 214500 ms for FLEX RES+
                - 2 to 214500 ms for FLEX STD
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if the time was changed successfully, False otherwise.
        """

        # Setting the ChangeIntegrationTime function
        function = getattr(uvvis_api, encrypted_function_names["ChangeIntegrationTime"])
        function.argtypes = [ctypes.c_int, ctypes.c_int]
        function.restype = ctypes.c_bool

        return function(int_time, FTHandle_ID)

    def get_YData(self, external_trigger: bool, FTHandle_ID: int):
        """
        Obtains a measurement.

        Args:
            external_trigger (bool):
                - True: Uses external trigger
                - False: Uses internal trigger
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            List[float]: Intensity values for each pixel.
        """

        # Setting the YData function
        function = getattr(uvvis_api, encrypted_function_names["YData"])
        function.argtypes = [ctypes.c_bool, ctypes.c_int]
        function.restype = ctypes.POINTER(ctypes.c_double)

        # Returns the the intensity of the pixels
        return function(external_trigger, FTHandle_ID)

    def get_XData(self, c0: float, c1: float, c2: float, c3: float, FTHandle_ID: int):
        """
        Gets wavelength array based on provided wavelength coefficients.

        Args:
            c0 (float): Wavelength coefficient c0
            c1 (float): Wavelength coefficient c1
            c2 (float): Wavelength coefficient c2
            c3 (float): Wavelength coefficient c3
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            list[float]: A list of wavelength values (in nm) for each pixel.

        Formula:
            Wavelength(PixelN) = c0 + c1 * PixelN + c2 * (PixelN ** 2) + c3 * (PixelN ** 3)
        """

        # Setting the XData function
        function = getattr(uvvis_api, encrypted_function_names["XData"])
        function.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_int,
        ]
        function.restype = ctypes.POINTER(ctypes.c_double)

        wavelengths = function(c0, c1, c2, c3, FTHandle_ID)

        # Calculate the number of pixels
        i = 0
        while wavelengths[i] != 0:
            i += 1
        n_pixels = i

        # Returns the wavelengths corresponding to the pixels
        return wavelengths[:n_pixels]

    def read_EEPROMCoeff(self, FTHandle_ID: int) -> float:
        """
        Reads the coefficients from the EEPROM of device.

        Args:
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            list[float]: A list containing four wavelength coefficients [c0, c1, c2, c3].
        """

        # Setting the ReadEEPROMCoeff function
        function = getattr(uvvis_api, encrypted_function_names["ReadEEPROMCoeff"])
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.POINTER(ctypes.c_double)

        # Returns the wavelength coefficients saved on the EEPROM
        return function(FTHandle_ID)[:4]

    def switch_shutter(self, switch: bool, FTHandle_ID: int) -> bool:
        """
        Closes or opens the shutter of device, if available.

        Args:
            switch (bool): True to close, False to open
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if successful, False otherwise.
        """

        # Setting the Shutter function
        function = getattr(uvvis_api, encrypted_function_names["Shutter"])
        function.argtypes = [ctypes.c_bool, ctypes.c_int]
        function.restype = ctypes.c_bool

        return function(switch, FTHandle_ID)

    def trigger_out_on_off(self, switch: bool, FTHandle_ID: int):
        """
        Enables or disables the device's trigger out function.

        Args:
            switch (bool): True to enable, False to disable
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if successful, False otherwise.
        """

        # Setting the TriggerOutOnOff function
        function = getattr(uvvis_api, encrypted_function_names["TriggerOutOnOff"])
        function.argtypes = [ctypes.c_bool, ctypes.c_int]
        function.restype = ctypes.c_bool

        return function(switch, FTHandle_ID)

    def trigger_in_enable(self, trigger_in_delay: int, FTHandle_ID: int) -> bool:
        """
        Activates Trigger In mode, allowing measurements based on external triggers.

        Args:
            trigger_in_delay (int): Delay in microseconds before responding to trigger
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if activated, False otherwise.
        """

        # Setting the TriggerInEnable function
        function = getattr(uvvis_api, encrypted_function_names["TriggerInEnable"])
        function.argtypes = [ctypes.c_int, ctypes.c_int]
        function.restype = ctypes.c_bool

        return function(trigger_in_delay, FTHandle_ID)

    def trigger_in_disable(self, FTHandle_ID: int) -> bool:
        """
        Deactivates Trigger In mode.

        Args:
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if disabled successfully, False otherwise.
        """

        # Setting the TriggerInDisable function
        function = getattr(uvvis_api, encrypted_function_names["TriggerInDisable"])
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.c_bool

        # Attempts to disable external trigger mode
        success = function(FTHandle_ID)

        if success:
            # Clean data output
            self.get_YData(False, FTHandle_ID)

        # Returns whether it was successful or not (True/False)
        return success

    def prepare_SpecACK(self, FTHandle_ID: int) -> bool:
        """
        Prepares the spectrometer for a new measurement using an external trigger.

        Args:
            FTHandle_ID (int): FTHandle_ID of the device

        Returns:
            bool: True if successful, False otherwise.
        """

        # Setting the SpecACK function
        function = getattr(uvvis_api, encrypted_function_names["SpecACK"])
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.c_bool

        return function(FTHandle_ID)


if __name__ == "__main__":
    import time
    import numpy as np
    import matplotlib.pyplot as plt

    uvvis = UVvis()

    # Test DLL presence
    uvvis.lib_test()

    device_info = uvvis.scan_devices()  # Get information of connected FLEX devices

    print(f"device_info: {device_info}")

    n_devices = device_info[0]  # Index 0 contains the number of connected devices

    print(n_devices)

    if n_devices != 0:

        for n in range(n_devices):

            ID = device_info[1 + 2 * n]  # Odd indexes contain the IDs

            print(uvvis.get_serial(ID))

            # Even natural indexes contain the number corresponding to the type of FLEX device
            FLEX_type_n = device_info[2 * (n + 1)]

            print(FLEX_types[FLEX_type_n])

        # Connect to the first device on the list
        ID = device_info[1]
        print(ID)
        FLEX_type_n = device_info[2]

        # Connects and gets handle to use with other functions
        FThandle_ID = uvvis.connect(0)
        print(FThandle_ID)
        if FThandle_ID != -1:  # Test if the connection was successful

            uvvis.switch_LED(True, FThandle_ID)  # Turn the LED on

            # Change integration time to the lowest value possible
            if FLEX_type_n == 0:
                integration_time = 2
            else:
                integration_time = 3
            uvvis.change_integration_time(1000, FThandle_ID)

            # Get wavelenth array (list type)
            c0, c1, c2, c3 = uvvis.read_EEPROMCoeff(FThandle_ID)
            wavelengths = uvvis.get_XData(c0, c1, c2, c3, FThandle_ID)
            n_pixels = len(wavelengths)

            uvvis.trigger_in_disable(FThandle_ID)  # Internal trigger mode

            uvvis.trigger_out_on_off(False, FThandle_ID)  # Trigger out disabled

            # Dark measurement
            uvvis.switch_shutter(True, FThandle_ID)  # Close shutter
            time.sleep(0.1)
            # Perform a measurement
            dark = uvvis.get_YData(False, FThandle_ID)[:n_pixels]
            uvvis.switch_shutter(False, FThandle_ID)  # Open shutter
            time.sleep(0.1)

            # Internal trigger measureme
            spectrum = uvvis.get_YData(False, FThandle_ID)[:n_pixels]

            # External trigger example with trigger out
            """
            TriggerOutOnOff(True, FThandle_ID) # Trigger out enabled

            TriggerInEnable(0, FThandle_ID) # External trigger mode

            SpecACK(FThandle_ID) # Ready the spectrometer for the next trigger

            input("Press Enter after external trigger! ")

            spectrum = YData(True, FThandle_ID)[:n_pixels] # External trigger measurement

            TriggerOutOnOff(False, FThandle_ID) # Trigger out disabled
            """

            spectrum_minus_dark = np.array(spectrum) - np.array(dark)  # Removing dark

            # Plotting the spectrum
            plt.subplots()
            plt.plot(wavelengths, spectrum_minus_dark)
            plt.xlabel(r"$\lambda$ (nm)")
            plt.ylabel("Intensity (counts)")
            plt.xlim(wavelengths[0], wavelengths[-1])
            plt.ylim(
                np.min(spectrum_minus_dark)
                - 0.05 * (np.max(spectrum_minus_dark) - np.min(spectrum_minus_dark)),
                np.max(spectrum_minus_dark)
                + 0.05 * (np.max(spectrum_minus_dark) - np.min(spectrum_minus_dark)),
            )
            plt.show()

            uvvis.switch_LED(False, FThandle_ID)
            # Disconnecting
            ID = uvvis.disconnect(FThandle_ID)
