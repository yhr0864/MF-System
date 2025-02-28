# from mf_system.hardware.devices.uv_vis_lib.uvvissdk import uvvisremotecontrol


class UV_Vis:
    def test_lib():
        pass


if __name__ == "__main__":
    # uvvis = UV_Vis()
    # print(uvvis.test_lib())
    import pefile
    import os

    def get_architecture(file_path):
        pe = pefile.PE(file_path)
        machine = pe.FILE_HEADER.Machine
        if machine == 0x014C:
            return "32-bit (x86)"
        elif machine == 0x8664:
            return "64-bit (x64)"
        else:
            return f"Unknown: {hex(machine)}"

    dll_path = "C:/Users/Yu/Desktop/mf-system/src/mf_system/hardware/devices/uv_vis_lib/dll/SpecDLL.dll"
    # dll_32_path = "U:/projects/devices/UV Vis/SDK/Sample/SpecDLL.dll"

    cetoni_dll = "C:/Users/Yu/Desktop/mf-system/src/mf_system/hardware/devices/pump_lib/dll/LABBCAN_ANALOGIO_API.dll"

    print(
        f"{dll_path} is {get_architecture(dll_path)}, with size {os.path.getsize(dll_path)}B"
    )
    print(
        f"{cetoni_dll} is {get_architecture(cetoni_dll)}, with size {os.path.getsize(cetoni_dll)}B"
    )

    import platform

    print(platform.architecture())

    from ctypes import CDLL, windll, POINTER, c_int
    import ctypes

    # cetoni = windll.LoadLibrary(cetoni_dll)
    my_dll = windll.LoadLibrary(dll_path)

    name = ctypes.create_string_buffer(255)
    # cetoni.LCAIO_GetChanName(ctypes.c_longlong(), name, ctypes.sizeof(name))

    connect = getattr(my_dll, "?Connect@classSpec@specspace@@SAHH@Z")
    disconnect = getattr(my_dll, "?Disconnect@classSpec@specspace@@SA_NH@Z")
    led = getattr(my_dll, "?LED@classSpec@specspace@@SA_N_NH@Z")
    lib_test = getattr(my_dll, "?LibTest@classSpec@specspace@@SAXXZ")
    scan_device = getattr(my_dll, "?ScanDevices@classSpec@specspace@@SAPEAHXZ")

    lib_test()
    scan_device.restype = POINTER(c_int)
    arr = scan_device()
    print(arr[0], arr[1], arr[3])
    connect(0)
    arr = scan_device()
    print(arr[0], arr[1], arr[3])
    res = led(True, 0)
    print(res)
    # print(cetoni_dll)
    # print(dir(cetoni))
    # print(dir(my_dll))
    # os.add_dll_directory(dll_path)
    # dll = lib = ctypes.WinDLL(os.path.abspath(dll_path))

    # dll = ctypes.windll.LoadLibrary(dll_path)
